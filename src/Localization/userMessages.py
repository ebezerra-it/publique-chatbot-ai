import json
import os
import uuid
import logging

suported_languages = [
    { 
        "language": "português",
        "language_code": "pt-br"
    },
    { 
        "language": "english",
        "language_code": "en-us"
    },
    { 
        "language": "deutsch",
        "language_code": "de-de"
    },
    { 
        "language": "italiano",
        "language_code": "it-it"
    },
    { 
        "language": "español",
        "language_code": "es-es"
    },
    { 
        "language": "français",
        "language_code": "de-de"
    },
]

class UserMessages():

    user_messages: any
    logger: logging

    def __init__(self, logger: logging) -> None:

        self.logger = logger

        jsonMessagesPathName = os.path.join(os.path.dirname(os.path.realpath(__file__)), "", "user_messages.json")
        if not os.path.exists(jsonMessagesPathName):
            raise SystemError('Missing user messages json file: ' + jsonMessagesPathName)
        
        with open(jsonMessagesPathName, "r") as f:
            try:
                self.user_messages = json.load(f)
            except:
                raise SystemError('Wrong format in user messages json file:' + jsonMessagesPathName)
            
    def getUserMessage(self, message_code: str, languageCode: str) -> str:
        for usr_msg in self.user_messages:
            if str(usr_msg['message_code']).upper() == message_code.upper():
                for local_usr_msg in usr_msg['localized_messages']:
                    if str(local_usr_msg['language_code']).lower() == languageCode.lower():
                        return str(local_usr_msg['user_message'])
                    if str(local_usr_msg['language_code']).lower() == 'en-us':
                        default_user_message = str(local_usr_msg['user_message'])
                    
                return default_user_message
        
        errorMessage = 'Unable do find user message {message_code}. Please contact the administrator and provide the error code: {error_code}'.format(message_code=message_code, error_code=uuid.uuid4())
        self.logger.error(errorMessage)
        
        return errorMessage

 