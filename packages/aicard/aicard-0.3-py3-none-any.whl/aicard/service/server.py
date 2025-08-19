from aicard.card import ModelCard
from aicard.service.assistant import Assistant
from flask import Flask, abort, redirect, request, jsonify
from flasgger import Swagger
from threading import Lock, Thread
from aicard.service import users
from aicard.service import converters
from aicard.service.logger import Logger
import secrets
import time
from threading import Thread


def exists(condition, message):
    # empty strings are allowed
    if condition is not None and isinstance(condition, str): return condition
    if not condition: abort(404, description=message)
    return condition

class ModelCardEntry:
    def __init__(self, card: ModelCard, creator: str, conn):
        self.card = card
        self.creator = creator
        self.preview = card.to_html_card()
        self.lock = Lock()
        self.__is_completing = False
        self.__thread = None
        self.conn = conn
        self.card_id = None
        self.last_accessed = time.time()

    def touch(self):
        self.last_accessed = time.time()

    def commit_card(self):
        flattened = self.card.data.flatten()
        assert flattened, "Cannot commit an empty model card."
        assert self.card_id is not None, "Internal error: card_id has not been set for a cached card"
        columns = list(flattened.keys())
        values = [flattened[key] for key in columns]
        query = f'''
            UPDATE cards
            SET {", ".join(f'"{col}" = ?' for col in columns)}
            WHERE id = ?
        '''
        cursor = self.conn.cursor()
        cursor.execute(query, values + [self.card_id])
        self.conn.commit()

    def start_completion(self):
        self.lock.acquire()
        if self.__is_completing:
            self.lock.release()
            abort(409, description="An AI assistant is working on the model card")
        self.__is_completing = True
        self.lock.release()

    def check_completion(self):
        self.lock.acquire()
        ret = self.__is_completing
        self.lock.release()
        return ret

    def end_completion(self):
        self.lock.acquire()
        self.__is_completing = False
        self.lock.release()

    def __enter__(self):
        self.lock.acquire()
        if self.__is_completing:
            self.lock.release()
            abort(409, description="An AI assistant is working on the model card")
        return self.card

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()

    def __autocomplete(self, url: str, assistant: Assistant):
        assistant.complete(self.card, url)
        self.end_completion()

    def __autorefine(self, assistant: Assistant):
        assistant.refine(self.card)
        self.end_completion()

    def autocomplete(self, url: str, assistant: Assistant):
        self.start_completion()
        self.__thread = Thread(target=self.__autocomplete, args=(url,assistant))
        self.__thread.start()
        return "submitted"

    def autorefine(self, assistant: Assistant):
        self.start_completion()
        self.__thread = Thread(target=self.__autorefine, args=(assistant,))
        self.__thread.start()
        return "submitted"

    def get_status(self):
        if self.check_completion(): return {"status": "locked", "message": "AI assistant is working on the model card"}
        return {"status": "editable", "message": "You can edit the model card"}

def serve(
    redirect_index,
    assistants: dict[str, Assistant],
    admin_username: str = "admin",
    admin_password: str = "admin",
    token_expiration_secs: int = 60*60,
    root:str|None = "db", # None or "" initializes a non-persistent database for testing
    log_file:str|None = None # None or "" uses the console for logging
):
    card_cache_lock = Lock()
    logger = Logger(log_file)
    token2expiration = dict()
    token2user = dict()
    conn = users.UserDB(logger=logger, root=root)
    app = Flask(__name__)
    empty_card = ModelCard()
    swagger = Swagger(app, template = {
        "swagger": "2.0",
        "info": {"title": "ModelCard",
            "description": "API docs",
            "version": "0.0.3"
        }
    })
    card_cache: dict[int, ModelCardEntry | None] = dict()
    def find_card(card_id: int):
        assert isinstance(card_id, int), "Card identifier must be an integer"
        with card_cache_lock:
            card = card_cache.get(card_id, None)
            card.touch()
            if card is None:
                # load the card from the database
                cursor = conn.conn.cursor()
                cursor.execute("SELECT * FROM cards WHERE id = ?", (card_id,))
                row = cursor.fetchone()
                if row:
                    col_names = [desc[0] for desc in cursor.description]
                    flattened = dict(zip(col_names, row))
                    card_creator = flattened.pop("user", "")
                    flattened.pop("id", None)
                    model_card = ModelCard()
                    model_card.data.assign_flattened(flattened)
                    card = ModelCardEntry(model_card, card_creator, conn)
                    card.card_id = card_id
                    card_cache[card_id] = card
        return card

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(str(e))
        return jsonify(error="Internal server error"), 500

    @app.errorhandler(Exception)
    def handle_unexpected_exception(e):
        logger.error(str(e))
        return jsonify(error="Unexpected server error"), 500

    @app.route("/", methods=['GET'])
    def get_index():
        return redirect(redirect_index, code=307)

    @app.route('/users', methods=['GET'])
    @users.require_admin(token2expiration)
    def admin_dashboard(token: str):
        """
        Retrieves all active and pending users.
        Requires a valid admin bearer token in the Authorization header.
        ---
        tags:
          - Admin
        parameters:
          - name: Authorization
            in: header
            type: string
            required: true
            description: Bearer token for admin authentication (e.g., "Bearer <token>")
        responses:
          200:
            description: Lists of all users and pending registrations.
            schema:
              type: object
              properties:
                users:
                  type: array
                  items:
                    type: object
                    properties:
                      username:
                        type: string
                      email:
                        type: string
                pending:
                  type: array
                  items:
                    type: object
                    properties:
                      username:
                        type: string
                      email:
                        type: string
          401:
            description: Unauthorized — missing token or invalid token format.
          403:
            description: Unauthorized — token expired or not valid.
        """
        def fetch_all_users(table_name: str):
            cursor = conn.conn.cursor()
            cursor.execute(f"SELECT username, email FROM {table_name}")
            rows = [{"username": u, "email": e} for u, e in cursor.fetchall()]
            return rows

        return jsonify({
            "users": fetch_all_users("users"),
            "pending": fetch_all_users("pending_users")
        })

    @app.route('/users/<string:username>', methods=['DELETE'])
    @users.require_admin(token2expiration)
    def delete_user(username, token: str):
        """
        Deletes a user or pending user by username.
        Requires a valid admin bearer token in the Authorization header.
        ---
        tags:
          - Admin
        parameters:
          - name: username
            in: path
            type: string
            required: true
            description: The username to delete.
          - name: Authorization
            in: header
            type: string
            required: true
            description: Bearer token for admin authentication (e.g., "Bearer <token>")
        responses:
          200:
            description: Successfully deleted the user.
            schema:
              type: object
              properties:
                deleted:
                  type: string
                  description: The username that was deleted.
          401:
            description: Unauthorized — missing or invalid token.
          403:
            description: Token expired or not valid for admin access.
          404:
            description: User not found.
        """
        deleted = False
        for table_name in ['users', 'pending_users']:
            cur = conn.conn.execute(f"DELETE FROM {table_name} WHERE username = ?", (username,))
            if cur.rowcount: deleted = True
            conn.conn.commit()
        if not deleted: abort(404, description="User not found")
        logger.warn(username+" - deleted")
        return jsonify({"deleted": username})

    @app.route('/users/<string:username>/accept', methods=['POST'])
    @users.require_admin(token2expiration)
    def promote_user(username, token: str):
        """
        Promotes a pending user to an active user.
        Requires a valid admin bearer token in the Authorization header.
        ---
        tags:
          - Admin
        parameters:
          - name: username
            in: path
            type: string
            required: true
            description: The username to promote.
          - name: Authorization
            in: header
            type: string
            required: true
            description: Bearer token for admin authentication (e.g., "Bearer <token>")
        responses:
          200:
            description: User was successfully promoted.
            schema:
              type: object
              properties:
                promoted:
                  type: string
                  description: The username that was promoted.
          401:
            description: Unauthorized — missing or invalid token.
          403:
            description: Token expired or not valid for admin access.
          404:
            description: Pending user not found.
        """
        cursor = conn.conn.cursor()
        cursor.execute("SELECT username, email, password FROM pending_users WHERE username = ?",(username,))
        row = cursor.fetchone()
        if not row: abort(404, description="Pending user not found")
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",(row[0], row[1], row[2]))
        cursor.execute("DELETE FROM pending_users WHERE username = ?",(username,))
        conn.conn.commit()
        return jsonify({"promoted": username})

    @app.route("/register", methods=["POST"])
    def register_user():
        """
        Registers a new user into the pending approval list.
        Administrator acceptance is required for them to log in.
        ---
        tags:
          - Auth
        parameters:
          - name: body
            in: body
            required: true
            description: JSON object with username, email, and password.
            schema:
              type: object
              properties:
                username:
                  type: string
                email:
                  type: string
                password:
                  type: string
        responses:
          201:
            description: Successfully registered. Pending admin approval.
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: "pending approval"
          400:
            description: Missing required fields (username, email, or password).
          409:
            description: User already exists in active or pending list.
        """
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        if not username or not email or not password: return "Missing fields among username, email, or password", 400# abort(400, description="Missing fields among username, email, or password")
        if conn.find_user('users', username) or conn.find_user('pending_users', username): return "User already exists", 409 #abort(409, description="User already exists")
        conn.insert_user('pending_users', username, email, password)
        return jsonify({"status": "pending approval"}), 201

    @app.route("/login", methods=["POST"])
    def login_user():
        """
        Logs in a user or the admin and returns an expiring bearer token.
        ---
        tags:
          - Auth
        parameters:
          - name: body
            in: body
            required: true
            description: JSON object with username and password.
            schema:
              type: object
              properties:
                username:
                  type: string
                password:
                  type: string
        responses:
          200:
            description: Login successful; bearer token issued.
            schema:
              type: object
              properties:
                token:
                  type: string
                  description: Bearer token to be used in Authorization header.
                admin:
                  type: boolean
                  description: Whether the logged-in user is an admin.
                expires_in:
                  type: integer
                  description: Token expiration time in seconds.
          401:
            description: Invalid credentials.
        """
        data = request.get_json()
        username = data.get("username", "")
        password = data.get("password", "")
        if username == admin_username and password == admin_password:
            token = secrets.token_urlsafe(32)
            token2expiration[token] = time.time() + token_expiration_secs
            token2user[token] = username
            logger.warn("logged in as administrator", user=username)
            return jsonify({"token": token, "admin": True, "expires_in": token_expiration_secs})
        row = conn.find_user('users', username)
        if not row: abort(401, description="Invalid credentials")
        stored_hash = row[2]
        if not users.verify_password(password, stored_hash): abort(401, description="Invalid credentials")
        token = secrets.token_urlsafe(32)
        token2expiration[token] = time.time() + token_expiration_secs
        token2user[token] = username
        logger.info("logged in", user=username)
        return jsonify({"token": token, "admin": False, "expires_in": token_expiration_secs})

    @app.route('/cards', methods=['POST'])
    def get_cards():
        """
        Retrieves a list of model cards from the database while filtering for a search query and performing pagination.
        The results contain both card id, title, and descriptions, and the total number of pages
        for the particular pagination limit. If no query is provided, all cards will be considered.
        If no page size is provided, or if non-positive, 10 is assumed. If no page is provided,
        or if it's non-positive, 1 (the first page) is assumed.
        ---
        tags:
          - UI
        parameters:
          - name: query
            in: body
            type: string
            required: false
            description: Case-insensitive filter on card titles.
            example: "my card"
          - name: page
            in: body
            type: integer
            required: false
            default: 1
            description: Page number, starting from 1.
          - name: page_size
            in: body
            type: integer
            required: false
            default: 10
            description: Number of results per page.
        responses:
          200:
            description: A paginated list of card summaries.
            schema:
              type: object
              properties:
                results:
                  type: array
                  description: List of card summaries.
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                        description: Card identifier.
                      name:
                        type: string
                        description: Card title.
                      creator:
                        type: string
                        description: The creator's username.
                      desc:
                        type: string
                        description: Card description (e.g., completion percentage).
                pages:
                  type: integer
                  description: Total number of result pages.
        """
        data = request.get_json() or {}
        query = data.get('query', '').strip().lower()
        page = max(int(data.get('page', 1)), 1)
        page_size = max(int(data.get('page_size', 10)), 1)
        cursor = conn.conn.cursor()
        if query: cursor.execute("SELECT COUNT(*) FROM cards WHERE LOWER(title) LIKE ?", (f"%{query}%",))
        else: cursor.execute("SELECT COUNT(*) FROM cards")
        total = cursor.fetchone()[0]
        num_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size
        if query: cursor.execute("SELECT id, title, user, desc FROM cards WHERE LOWER(title) LIKE ? ORDER BY id LIMIT ? OFFSET ?", (f"%{query}%", page_size, offset))
        else: cursor.execute("SELECT id, title, user, desc FROM cards ORDER BY id LIMIT ? OFFSET ?", (page_size, offset))
        rows = cursor.fetchall()
        results = [{"id": row[0], "name": row[1], "creator": row[2], "desc": row[3]} for row in rows]
        return jsonify({"results": results, "pages": num_pages})

    @app.route('/assistants', methods=['GET'])
    @users.require_auth(token2expiration)
    def get_assistants(token: str):
        """
        Retrieves all available AI assistants for the current user and card, including their names and descriptions.
        ---
        tags:
          - UI
        responses:
            200:
                description: A list of assistants with their names and descriptions.
                schema:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                        description: The name of the assistant.
                      desc:
                        type: string
                        description: The description of the assistant.
        """
        return jsonify([{"name": key, "desc": value.description} for key, value in assistants.items()])

    @app.route('/card/<int:card_id>', methods=['GET'])
    def get_card(card_id):
        """
        Retrieves the JSON data for a given model card.
        ---
        tags:
          - UI
        parameters:
          - name: card_id
            in: path
            type: integer
            required: true
            description: The unique identifier for the model card.
        responses:
            200:
                description: The JSON representation of the model card.
                schema:
                  type: object
                  description: The model card contents. This includes fields title and a list of related card ids and names.
            404:
                description: The requested card does not exist or has been deleted.
            409:
                description: An AI assistant is working on the model card.
        """
        with exists(find_card(card_id), "Model card does not exist or has been deleted.") as card:
            return jsonify(converters.dict2dynamic(card.data|{"related": []}, {"title"}))

    @app.route('/card/<int:card_id>/locked', methods=['GET'])
    @users.require_auth(token2expiration)
    def get_card_locked_status(card_id, token: str):
        """
        Retrieves a string value explaining why the card is locked, for example by an AI assistant working on it.
        If the card is locked, post or put methods on the card will create errors.
        ---
        tags:
          - UI
        parameters:
          - name: card_id
            in: path
            type: integer
            required: true
            description: The card's unique identifier.
          - name: Authorization
            in: header
            type: string
            required: true
            description: Bearer token for user authentication (e.g., "Bearer <token>")
        responses:
            200:
                description: The description (e.g., LLM progress stage) of the mechanism currently locking the card.
                schema:
                  type: string
            401:
                description: Unauthorized — missing token or invalid token format.
            403:
                description: Unauthorized — token expired or not valid.
            404:
                description: The request's card does not exist or has been deleted.
        """
        card = exists(find_card(card_id), "Model card does not exist or has been deleted.")
        return jsonify("An AI assistant is working on the card" if card.check_completion() else "")

    @app.route('/card/<int:card_id>/title', methods=['GET'])
    def get_card_title(card_id):
        """
        Retrieves the title of the specified model card.
        ---
        parameters:
          - name: card_id
            in: path
            type: integer
            required: true
            description: The card's unique identifier.
        responses:
            200:
                description: The title of the model card.
                schema:
                  type: string
            404:
                description: The requested card does not exist or has been deleted.
            409:
                description: An AI assistant is working on the model card.
        """
        with exists(find_card(card_id), "Model card does not exist or has been deleted.") as card:
            return jsonify(card.title)

    @app.route('/card/<int:card_id>/title', methods=['PUT'])
    @users.require_auth(token2expiration)
    def set_card_title(card_id, token: str):
        """
        Updates the title of the specified model card.
        ---
        parameters:
          - name: card_id
            in: path
            type: integer
            required: true
            description: The card's unique identifier.
          - name: body
            in: body
            required: true
            schema:
              type: string
              example: "New model card title"
          - name: Authorization
            in: header
            type: string
            required: true
            description: Bearer token for user authentication (e.g., "Bearer <token>")
        responses:
            200:
                description: The updated title of the model card.
                schema:
                  type: string
            401:
                description: Unauthorized — missing token or invalid token format.
            403:
                description: Unauthorized — token expired or not valid.
            404:
                description: The requested card does not exist or has been deleted, or invalid request body.
            409:
                description: An AI assistant is working on the model card.
        """
        with exists(find_card(card_id), "Model card does not exist or has been deleted.") as card:
            json_data = request.get_json()
            exists(isinstance(json_data, str), "Can only send string data to update model card titles.")
            card.data['title'] = json_data
            return jsonify(card.data['title'])

    @app.route('/card/fields', methods=['GET'])
    def get_card_fields():
        """
        Lists all top-level field names for model cards that contain data entries.
        For example, this list does not contain the title but that it contains test datasets, training datasets, etc.
        This method helps the frontend be generalize-able in case there is a need for extensibility.
        Once fields are obtained, use /card/fields/<field_name> to retrieve its data entries.
        ---
        responses:
            200:
                description: List of top-level card field names.
                schema:
                    type: array
                    items:
                        type: string
        """
        return jsonify([key for key, value in empty_card.data.items() if isinstance(value, dict)])

    @app.route('/card/fields/<string:field_name>', methods=['GET'])
    def get_card_field_names(field_name):
        """
        Lists all data entry  names under the given field_name in a model card.
        ---
        parameters:
          - name: field_name
            in: path
            type: string
            required: true
            description: The top-level field name.
        responses:
            200:
                description: List of subfield names for the field.
                schema:
                    type: array
                    items:
                        type: string
            404:
                description: Field does not exist.
        """
        fields = empty_card.data
        field = exists(fields.get(field_name, None), f"Field '{field_name}' does not exist.")
        exists(isinstance(field, dict), f"Field '{field_name}' does not have data entries.")
        return jsonify(list(field.keys()))

    @app.route('/card/<int:card_id>/<string:field_name>/<string:data_name>', methods=['GET'])
    def get_card_field(card_id, field_name, data_name):
        """
        Retrieves an entry from card.field_name.data_name.
        For example, retrieve card.model.version.
        ---
        parameters:
          - name: card_id
            in: path
            type: integer
            required: true
            description: The card's identifier.
          - name: field_name
            in: path
            type: string
            required: true
            description: The card's field name. To see all field names available for cards get /card/fields.
          - name: data_name
            in: path
            type: string
            required: true
            description: The data entry name within the card's field To see all data entries available for the field get /card/fields/field_name.
        responses:
            200:
                description: A string containing an editable (markdown) version of data values.
                schema:
                  type: string
                  description: The card's editable string representation.
            404:
                description: Resource does not exist.
            409:
                description: An AI assistant is working on the model card.
        """
        with exists(find_card(card_id), "Model card does not exist or has been deleted.") as card:
            field = exists(card.data.get(field_name, None), "Invalid field name. Candidates: " + ','.join(card.data.keys()))
            data = exists(field.get(data_name, None), f"Invalid data name {data_name}. Candidates: " + ','.join(field.keys()))
            return jsonify(data)

    @app.route('/card/<int:card_id>/<string:field_name>/<string:data_name>', methods=['PUT'])
    @users.require_auth(token2expiration)
    def set_card_field(card_id, field_name, data_name, token: str):
        """
        Sets a value to card.field_name.data_name.
        ---
        parameters:
          - name: card_id
            in: path
            type: integer
            required: true
            description: The card's identifier.
          - name: field_name
            in: path
            type: string
            required: true
            description: The card's field name. To see all field names available for cards get /card/fields.
          - name: data_name
            in: path
            type: string
            required: true
            description: The data entry name within the card's field To see all data entries available for the field get /card/fields/field_name.
          - name: body
            in: body
            required: true
            description: A string to set as value.
            schema:
              type: string
          - name: Authorization
            in: header
            type: string
            required: true
            description: Bearer token for user authentication (e.g., "Bearer <token>")
        responses:
            200:
                description: A list of integer identifiers.
                schema:
                    type: array
                    items:
                        type: integer
            401:
                description: Unauthorized — missing token or invalid token format.
            403:
                description: Unauthorized — token expired or not valid.
            404:
                description: Resource does not exist, or invalid body.
            409:
                description: An AI assistant is working on the model card.
        """
        with exists(find_card(card_id), "Model card does not exist or has been deleted.") as card:
            field = exists(card.data.get(field_name, None), "Invalid field name. Candidates: " + ','.join(card.data.keys()))
            data = exists(field.get(data_name, None), f"Invalid data name {data_name}. Candidates: " + ','.join(field.keys()))
            json_data = request.get_json()
            exists(isinstance(json_data, str), "Can only send string data to update model card fields.")
            field[data_name] = json_data
            return jsonify(field[data_name])  # do not return json_data directly, as setting the value may format it


    @app.route('/card/<int:card_id>', methods=['DELETE'])
    @users.require_auth(token2expiration)
    def delete_card(card_id, token: str):
        """
        Removes the respective card; it will be considered a missing resource from now on.
        ---
        tags:
          - UI
        parameters:
          - name: Authorization
            in: header
            type: string
            required: true
            description: Bearer token for user authentication (e.g., "Bearer <token>")
        responses:
            204:
                description: Successfully removed.
            401:
                description: Unauthorized — missing token or invalid token format.
            403:
                description: Unauthorized — token expired or not valid.
            404:
                description: Resource does not exist.
        """
        with exists(find_card(card_id), "Model card does not exist or has been deleted.") as _:
            cursor = conn.conn.cursor()
            cursor.execute("DELETE FROM cards WHERE id = ?", (card_id,))
            conn.conn.commit()
            with card_cache_lock: del card_cache[card_id]
            logger.info("deleted a card", user=token2user.get(token, None))
            return '', 204

    @app.route('/card/<int:card_id>', methods=['PUT'])
    @users.require_auth(token2expiration)
    def update_card(card_id, token: str):
        """
        Updates a model card's contents - enables manual upload.
        The provided json data should be (parts of) a model card's
        json representation with potentially some missing fields, and updates everything in the
        target card. The card's contents after setting everything are returned. This operation
        is safe in that all fields should be valid in order for any to be set.
        ---
        tags:
          - UI
        parameters:
          - name: card_id
            in: path
            type: integer
            required: true
            description: The card's identifier.
          - name: body
            in: body
            required: true
            description: Partial or full model card JSON to update the card with. This can be either in the dynamic format used by this API or in a static format that is exported by the aicard library.
            schema:
              type: object
          - name: Authorization
            in: header
            type: string
            required: true
            description: Bearer token for user authentication (e.g., "Bearer <token>")
        responses:
            200:
                description: Successfully set everything and retrieves a json representation of the model card.
            401:
                description: Unauthorized — missing token or invalid token format.
            403:
                description: Unauthorized — token expired or not valid.
            404:
                description: Either the card or at least one of the provided fields do not exist.
            409:
                description: An AI assistant is working on the model card.
        """
        json_data = request.get_json()
        with exists(find_card(card_id), "Model card does not exist or has been deleted.") as card:
            try: card.data.assign(converters.dynamic2dict(json_data, {"title"}))
            except AssertionError as e: abort(404, "Wrong data: "+str(e))
            except Exception as e: abort(404, "Wrong data: "+str(e))
            logger.info("updated a card", user=token2user.get(token, None))
            return jsonify(converters.dict2dynamic(card.data, {"title"}))

    @app.route('/card', methods=['POST'])
    @users.require_auth(token2expiration)
    def create_card(token: str):
        """
        Creates a model card given an optional json representation - the representation is for manual upload.
        The provided json data should be either an empty dict or (parts of) a model card's
        json representation with potentially some missing fields, and updates everything in the
        target card. The card's contents after setting everything are retrieved.
        ---
        tags:
          - UI
        parameters:
          - name: body
            in: body
            required: false
            schema:
              type: object
              description: Binary encoding of a file loading the card.
          - name: Authorization
            in: header
            type: string
            required: true
            description: Bearer token for user authentication (e.g., "Bearer <token>")
        responses:
            201:
                description: Successfully set everything and retrieves a json representation of the model card.
            401:
                description: Unauthorized — missing token or invalid token format.
            403:
                description: Unauthorized — token expired or not valid.
            404:
                description: One of the provided fields do not exist.
            409:
                description: An AI assistant is working on the model card.
        """
        json_data = request.get_json()
        card = ModelCardEntry(ModelCard(), token2user.get(token, ""), conn)
        if json_data:
            try: card.card.data.assign(converters.dynamic2dict(json_data, {"title"}))
            except AssertionError as e:
                print("Assertion error: "+str(e))
                abort(500, description=str(e))
            except Exception as e:
                print("Exception: "+str(e))
                abort(500, description=str(e))
        flattened = card.card.data.flatten()
        columns = list(flattened.keys())
        creator = token2user.get(token, "")
        cursor = conn.conn.cursor()
        cursor.execute(f'''INSERT INTO cards (user, desc, {','.join(columns)}) VALUES (?,?, {",".join(["?"] * len(columns))})''',
                       [creator, ""] + [flattened[key] for key in columns])
        conn.conn.commit()
        card_id = cursor.lastrowid
        card.card_id = card_id
        with card_cache_lock:
            card_cache[card_id] = card
        logger.info("created a card", user=creator)
        return jsonify(card_id), 201

    @app.route('/assistant/<string:assistant_type>/complete/<int:card_id>', methods=['POST'])
    @users.require_auth(token2expiration)
    def autocomplete_card(card_id: int, assistant_type: str, token: str):
        """
        Autocompletes an already created model card given a string pointing to a repository URL or some file contents.
        This calls on an AI assistant to work on the card, blocking editing while the latter runs.
        ---
        tags:
          - UI
        parameters:
          - name: card_id
            in: path
            type: integer
            required: true
            description: The card's identifier.
          - name: assistant_type
            in: path
            type: string
            required: true
            description: The AI assistant type. Options available from get /assistants.
          - name: body
            description: A repository url starting with http:// or https://, or an uploaded readme text file's contents (can be the contents of a .txt, .md, or .html file).
            in: body
            required: true
            schema:
              type: string
          - name: Authorization
            in: header
            type: string
            required: true
            description: Bearer token for user authentication (e.g., "Bearer <token>")
        responses:
            200:
                description: Successfully submitted task.
            401:
                description: Unauthorized — missing token or invalid token format.
            403:
                description: Unauthorized — token expired or not valid.
            404:
                description: Resource does not exist.
            409:
                description: An AI assistant is working on the model card.
        """
        json_data = request.get_json()
        assistant = exists(assistants.get(assistant_type, None), "Assistant not available")
        exists(isinstance(json_data, str), "Autocomplete requires a url string as POST data")
        status = exists(find_card(card_id), "Model card does not exist or has been deleted.").autocomplete(json_data, assistant)
        logger.info("requested an autocompletion from "+assistant_type, user=token2user.get(token, None))
        return jsonify(status)

    @app.route('/assistant/<string:assistant_type>/refine/<int:card_id>', methods=['POST'])
    @users.require_auth(token2expiration)
    def autorefine_card(card_id: int, assistant_type: str, token: str):
        """
        Refines an already created model card so that its contents are easier to parse by laypeople.
        This calls on an AI assistant to work on the card, blocking editing while the latter runs.
        ---
        tags:
          - UI
        parameters:
          - name: card_id
            in: path
            type: integer
            required: true
            description: The card's identifier.
          - name: assistant_type
            in: path
            type: string
            required: true
            description: The AI assistant type. Options available from get /assistants.
          - name: Authorization
            in: header
            type: string
            required: true
            description: Bearer token for user authentication (e.g., "Bearer <token>")
        responses:
            200:
                description: Successfully submitted task.
            401:
                description: Unauthorized — missing token or invalid token format.
            403:
                description: Unauthorized — token expired or not valid.
            404:
                description: Resource does not exist.
            409:
                description: An AI assistant is working on the model card.
        """
        assistant = exists(assistants.get(assistant_type, None), "Assistant not available")
        status = exists(find_card(card_id), "Model card does not exist or has been deleted.").autorefine(assistant)
        logger.info("requested a card refinement from "+assistant_type, user=token2user.get(token, None))
        return jsonify(status)

    @app.route('/docs', methods=['GET'])
    def docs():
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint == 'static':  continue
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            routes.append({
                "endpoint": rule.endpoint,
                "methods": methods,
                "path": str(rule),
            })
        return jsonify(routes)

    def gc():
        while True:
            now = time.time()
            one_hour = 3600
            to_delete = []
            with card_cache_lock:
                for card_id, entry in list(card_cache.items()):
                    if entry is None:
                        to_delete.append(card_id)
                        continue
                    entry.lock.acquire()
                    try:
                        if not entry.check_completion() and now - entry.last_accessed > one_hour:
                            to_delete.append(card_id)
                    finally: entry.lock.release()
                for card_id in to_delete: card_cache.pop(card_id, None)
            time.sleep(600)  # run every 10 minutes

    logger.ok("Server is ready.")
    return app, gc
