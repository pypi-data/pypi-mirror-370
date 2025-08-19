import requests
import json
from aicard.service.logger import Logger
from aicard.card.model_card import ModelCard

class CardConnector():
    def __init__(self, id: int, client: "Client", prototype: ModelCard):
        self.id = int(id)
        self.client = client
        self.prototype = ModelCard()
        self.prototype.data.assign(prototype.data)

class Client():
    def __init__(self, url, token, logger:Logger|str|None=None):
        self.url = url
        self.token = token
        self.logger = Logger() if logger is None else Logger(logger) if isinstance(logger, str) else logger
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def create(self, data=None):
        if data is None: data = ModelCard()
        assert isinstance(data, ModelCard), "For now, you can only create a model card given another model card through while using the client api"
        prototype = data
        response = self.post("/card", json=prototype.data)
        if response.status_code != 201: self.logger.fatal(f"Card creation failed: {response.status_code} {response.text}")
        card_id = response.json()
        new_card = ModelCard(connector=CardConnector(card_id, self, prototype))
        new_card.data.assign(prototype.data)
        return new_card

    def get(self, path: str, **kwargs):
        return self.session.get(f"{self.url}{path}", **kwargs)

    def post(self, path: str, json=None, **kwargs):
        return self.session.post(f"{self.url}{path}", json=json, **kwargs)

    def delete(self, path: str, **kwargs):
        return self.session.delete(f"{self.url}{path}", **kwargs)

    def put(self, path: str, json=None, **kwargs):
        return self.session.put(f"{self.url}{path}", json=json, **kwargs)


def connect(url, username, password, logger:Logger|str|None=None):
    login_url = url.rstrip("/") + "/login"
    response = requests.post(login_url, json={"username": username, "password": password})
    logger = Logger() if logger is None else Logger(logger) if isinstance(logger, str) else logger
    if response.status_code != 200: logger.fatal(f"Login failed: {response.status_code} {response.text}")
    client = Client(url=url.rstrip("/"), token=response.json()["token"], logger=logger)
    client.logger.info(f"Connected to server\n * User: {username}\n * Server: {client.url}")
    return client
