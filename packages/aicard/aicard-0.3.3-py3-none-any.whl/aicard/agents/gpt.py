import openai
import os
from aicard.agents.agent import Agent


class GPT(Agent):
    tasks = {
        "summarization": "You are a helpful assistant that summarizes documents.",
        "completion": "You are a helpful assistant completes json fields of a model card."
    }

    def __init__(self, model='gpt-3.5-turbo', max_tokens=4000, temperature=0.7, top_p=1):
        # gpt-3.5-turbo gpt-4
        self._model = model
        openai.api_key = os.getenv("OPENAI_API_KEY")
        assert openai.api_key, "Can't find OPENAI_API_KEY in the environment."
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

    def _run(self, content: str, task: str):
        assert isinstance(content, str), "content must be of type str"
        assert task in GPT.tasks, "Not supported task: "+task
        response = openai.chat.completions.create(
            model=self._model,
            messages= [{"role": "system", "content": GPT.tasks[task]}, {"role": "user", "content": content}],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p
        )
        return response.choices[0].message.content
