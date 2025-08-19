class Agent:
    def _run(self, content: str, task: str): raise NotImplementedError("This is an abstract agent class")
    def summarization(self, content: str): return self._run(content, task="summarization")
    def completion(self, content: str): return self._run(content, task="completion")
