import re
from importlib.resources import read_text as read
from jinja2 import Environment, BaseLoader
from aicard.card.dot_dict import DotDict


class HTMLRenderer:
    def __init__(self, data: DotDict, editable: bool=False):
        self.data = data
        self.tabs = []
        self.model_details = ""
        self.title = ""
        package = "aicard.card.traits.html_template"
        template = (
            read(package, "template.html")
            .replace(
                """<link rel="stylesheet" href="template.css">""",
                "<style>" + read(package, "template.css") + "</style>",
            )
            .replace(
                """<script src="template.js"></script>""",
                "<script>" + read(package, "template.js") + "</script>",
            )
        )
        if editable:
            template = template.replace("<body>", """<body contenteditable = "true">""")
        self.template_env = Environment(loader=BaseLoader())
        self.template = self.template_env.from_string(template)

    def __add_show_more_info(self, title, content):
        show_more_html = f"""
	    <div class="show-more-container">
	        <button class="show-more-btn" onclick="toggleShowMoreContent(this)">{title}</button>
	        <div class="show-more-content" style="display: none;">
	            {content}
	        </div>
	    </div>
	    """
        return show_more_html

    def __process_moreinfo_sections(self, input_string):
        def recursive_replace(string):
            pattern = r"<moreinfo>(.*?)</moreinfo>"
            def replace_match(match):
                content = match.group(1)
                content = recursive_replace(content)
                return self.add_show_more_info("+", content)
            return re.sub(pattern, replace_match, string, flags=re.DOTALL)
        return recursive_replace(input_string)

    def __json2html(self, data, level=1):
        html_content = ""
        if isinstance(data, dict):
            for key, value in data.items():
                key = key.replace('_', ' ')
                if isinstance(value, (dict, list)):
                    html_content += f"<h{level}>{key}</h{level}>"
                    html_content += self.__json2html(value, level + 1)
                else:
                    if key == "plot": html_content += f"{value}"
                    elif key == "description": html_content += f"<p>{value}</p>"
                    else:
                        value = value if value else '<span class="value_missing">---</span>'
                        html_content += f"<p><span class=\"key_entry\">{key}</span> {value}</p>"
        elif isinstance(data, list):
            html_content += "<ul>"
            for item in data: html_content += f"<li>{self.__json2html(item, level)}</li>"
            html_content += "</ul>"
        elif isinstance(data, str):
            html_content += f'<img src="{data}" alt="Image" style="max-width:100%;height:auto;">' \
                            if data.startswith(("data:image/png;base64,", "data:image/jpeg;base64,")) \
                            else  f"<p>{data}</p>"
        else:
            html_content += f"<p>{data}</p>"
        if html_content=="<p></p>":
            html_content = '<p><span class="value_missing">---</span></p>'
        return html_content

    def render(self):
        return self.template.render(
            title=self.data.title,
            model_details=self.__json2html(self.data.model),
            tabs=[{"name": k.replace("_", " "), "content": self.__json2html(v)}
                  for k,v in self.data.items() if k!="title" and k!="model"]
        )
