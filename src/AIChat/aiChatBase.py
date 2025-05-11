from abc import ABC, abstractmethod
from Context.contextBase import ContextBase, ContextData
import logging

class AIChatBase(ABC):

    @property
    def logger(self) -> logging:
        return self.__logger
    
    @property
    def context(self) -> ContextBase:
        return self.__context

    @abstractmethod
    def __init__(self, logger: logging, context: ContextBase) -> None:
        super().__init__()
        self.__logger = logger
        self.__context = context

    @abstractmethod
    def updateContextData(self) -> bool:        
        return self.context.updateContextData()

    @abstractmethod
    def askAIChat(self, question, language_code='pt-br') -> str:
        ...
