from abc import ABC, abstractmethod
from io import BytesIO
import requests
from Localization.userMessages import UserMessages
import logging
import os

class ChatInterfaceBase(ABC):
    
    @property
    def logger(self) -> logging:
        return self.__logger
    
    @property
    def userMessages(self) ->  UserMessages:
        return self.__userMessages
    
    @property
    def audioMimeType(self) ->  str:
        return self.__audioMimeType
    

    def __init__(self, logger: logging, audioMimeType: str) -> None:
        super().__init__()
        self.__logger = logger
        self.__audioMimeType = audioMimeType

        try:
            self.__userMessages = UserMessages(logger)
        except SystemError as e:
            self.logger.fatal(str(e))
            exit(1)


    def apiSendTextMessage(self, textMessage: str) -> str:
        if len(textMessage.strip()) < 10:
            raise SystemError('Text message too short')
        
        form_data = { "textMessage" : textMessage }
        
        responseData = requests.post(url=os.getenv("API_SENDTEXTMESSAGE_URL"), data=form_data)
        responseJson = responseData.json()
        
        return responseJson['answer']


    def apiSendVoiceMessage(self, audioStream: any, filename: str, mimeType: str) -> any:
        responseData = requests.post(os.getenv("API_SENDVOICEMESSAGE_URL"), 
            files={ 'file': audioStream }
        )
        return responseData.content


    def apiWelcome(self, languageCode = "", userFirstname = "") -> str:
        params = { 
            "languageCode" : languageCode,
            "userFirstname" : userFirstname
        }
        responseData = requests.get(url=os.getenv("API_WELCOME_URL"), params=params)
        responseJson = responseData.json()
        
        return responseJson['message']
    

    def apiSetLanguage(self, languageCode: str) -> str:
        params = { "language_code" : languageCode }
        
        responseData = requests.get(url=os.getenv("API_SETLANGUAGE_URL"), params=params)
        responseJson = responseData.json()
        
        return responseJson['language_code']
    

    def apiSetUserFirstName(self, firstName: str) -> str:
        params = { "first_name" : firstName }
        
        responseData = requests.get(url=os.getenv("API_SET_USER_FIRSTNAME_URL"), params=params)
        responseJson = responseData.json()
        
        return responseJson['user_firstname']
    