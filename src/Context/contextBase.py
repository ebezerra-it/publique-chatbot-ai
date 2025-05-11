from abc import ABC, abstractmethod
import hashlib



class ContextData:

    def __init__(self, data='') -> None:
        if data == '':
            self.__data = ''
            self.__checksum = ''
        else:
            self.data = data

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data):
        self.__data = data
        self.__checksum = hashlib.md5(self.__data.encode('utf-8')).hexdigest()

    @property
    def checksum(self):
        return self.__checksum
    

class ContextBase(ABC):

    @abstractmethod
    def __init__(self) -> None:
        super().__init__()
        self.contextData = ContextData()

    @property
    def contextData(self) -> ContextData:
        return self.__contextData

    @contextData.setter
    def contextData(self, contextData) -> None:
        self.__contextData = contextData


    def updateContextData(self) -> bool:
        context = self.loadContextData()

        if context.data.strip() == '':
            raise ValueError('Empty context data')
        
        if context.checksum == self.__contextData.checksum:
            return False

        self.__contextData = context
        return True


    @abstractmethod
    def loadContextData(self) -> ContextData:
        ...