import time
from aicard.card import ModelCard


class Assistant:
    def __init__(self, description=None):
        self.description = description
    def complete(self, card: ModelCard, url: str): pass
    def refine(self, card: ModelCard): pass

class TestAssistant(Assistant):
    def __init__(self, delay: float=0):
        super().__init__(description="<h1>Test assistant</h1>This AI assistant is primarily used for testing. For now, it does nothing, but some simple ad-hoc functionality for autocompleting and refining model cards may be added.")
        self.delay = delay
    def complete(self, card: ModelCard, url: str):
        if self.delay: time.sleep(self.delay)
    def refine(self, card: ModelCard):
        if self.delay: time.sleep(self.delay)
