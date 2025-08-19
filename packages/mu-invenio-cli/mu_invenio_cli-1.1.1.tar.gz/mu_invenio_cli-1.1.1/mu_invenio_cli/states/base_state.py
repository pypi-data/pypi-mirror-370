from abc import ABC, abstractmethod


class BaseState(ABC):
    def __init__(self, context):
        self.context = context

    @abstractmethod
    def handle(self):
        pass
