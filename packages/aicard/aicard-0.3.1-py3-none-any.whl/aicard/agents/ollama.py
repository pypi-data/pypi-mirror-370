import requests
import json
from aicard.agents.agent import Agent


class Ollama(Agent):
    tasks = {
        "summarization": "You are a helpful assistant that summarizes documents.",
        "completion": "You are a helpful assistant completes json fields of a model card."
    }

    def __init__(self, model: str='llama3.2:3b', base_url: str="http://localhost:11434"):
        self._base_url = base_url
        self._url = f"{base_url}/api/chat"
        self._model = model
        test = requests.post(self._url, json={
            "model": model,
            "stream": False,
            "messages": [{"role": "user", "content": "Request test"}]
        })
        assert test.status_code == 200, f"Failed to initialize model '{model}'\nResponse: {test.text}"
        self.max_tokens = 4000

    def _run(self, content: str, task: str):
        assert isinstance(content, str), "Content must be of type str"
        assert task in Ollama.tasks, "Not supported task: "+task
        response = requests.post(self._url, json={
            "model": self._model,
            "stream": False,
            "messages": [{"role": "system", "content": Ollama.tasks[task]}, {"role": "user", "content": content}]
        })
        return json.loads(response.text)["message"]["content"]
