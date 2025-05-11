from fastapi import APIRouter, File, Body, HTTPException, Request, Depends, Response, UploadFile
from fastapi.responses import StreamingResponse, FileResponse
from typing import Annotated, Optional
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ApiServices.Routes.Auth import auth
from dotenv import load_dotenv
from io import BytesIO
import os
import logging
from Context.contextPublique import ContextPublique
from Text2Speech.text2SpeechGoogleCloud import Text2SpeechGoogleCloud
from Speech2Text.speech2TextGoogleGemini import Speech2TextGoogleGemini
from Speech2Text.speech2TextBase import Transcription
from AIChat.aiChatGoogleGemini import AIChatGoogleGemini
from Localization.userMessages import UserMessages, suported_languages

import google.generativeai as genai # type: ignore


load_dotenv()

loglevel = {
    'NONE' : logging.NOTSET,
    'NOTSET' : logging.NOTSET,
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARN': logging.WARN,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
}.get(os.getenv("LOGGING_LEVEL"), logging.INFO)
logging.basicConfig(
   # filename='publique-chabot-ai.log',
   # filemode='a',
    level=loglevel, 
    format='%(asctime)s - %(levelname)s - %(message)s')

chatbothRouter = APIRouter()

contextPublique = ContextPublique(os.getenv("PUBLIQUE_CONTEXT"))
text2speech = Text2SpeechGoogleCloud()


genai.configure(api_key=os.getenv("GOOGLE_GEMINI_APIKEY"))
model = genai.GenerativeModel(os.getenv("GOOGLE_GEMINI_MODEL"))

speech2Text = Speech2TextGoogleGemini(genai, model)

aichat = AIChatGoogleGemini(logging, genai, model, contextPublique)

userMessages = UserMessages(logging)

user_language_code = str(os.getenv("API_DEFAULT_LANGUAGE_CODE"))

user_firstname = userMessages.getUserMessage("NON_IDENTIFIED_USERNAME", user_language_code)


@chatbothRouter.get("/setLanguage")
def setLanguage(language_code: Annotated[str, Body()]):
    global user_language_code
    user_language_code = next((language for language in suported_languages if language['language_code'] == language_code), None)
    user_language_code = 'en-us' if not user_language_code else user_language_code

    return {
        "status": "ok",
        "message": f"User language set to: {user_language_code}"
    }


@chatbothRouter.get("/setUserFirstName")
def setUserFirstName(userFirstName: Annotated[str, Body()]):
    user_firstname = userFirstName

    return {
        "status": "ok",
        "message": f"User first name set to: {user_firstname}"
    }


@chatbothRouter.post("/sendTextMessage")
async def sendTextMessage(textMessage: Annotated[str, Body()]):
    try:
        result = aichat.askAIChat(textMessage)
    except Exception as e:
        logging.error('An error occurred in SendTextMessage: ' + str(e))
        raise HTTPException(status=500, detail='An error occurred in SendTextMessage: ' + str(e))

    return {
        "status": "ok",
        "answer": result
    }


@chatbothRouter.get("/welcome")
async def welcomeMessage(userFirstname: Optional[str] = None, languageCode: Optional[str] = None):
    global user_language_code
    if languageCode:
        user_language_code = next((language['language_code'] for language in suported_languages if language['language_code'] == languageCode), None)
        user_language_code = str(os.getenv("API_DEFAULT_LANGUAGE_CODE")) if not user_language_code else user_language_code
    
    global user_firstname
    if userFirstname:
        user_firstname = userFirstname
    else:
        user_firstname = userMessages.getUserMessage("NON_IDENTIFIED_USERNAME", user_language_code)


    return {
        "status": "ok",
        "message": userMessages.getUserMessage(
                "WELCOME_MESSAGE",
                user_language_code
            ).format(user=user_firstname)
    }


@chatbothRouter.post("/sendVoiceMessage")
async def sendVoiceMessagefile(response: Response, file: Annotated[bytes, File()]):
    try:
        transcript = speech2Text.getTranscription(
            os.getenv("APISERVICE_AUDIO_MIME_TYPE"), 
            audioStream=BytesIO(file))
        
        aiChatAnswer = aichat.askAIChat(transcript.text, transcript.language_code)

    except Exception as e:
        logging.error('An error occurred in SendVoiceMessage: ' + str(e))
        raise HTTPException(status=500, detail='An error occurred in SendVoiceMessage: ' + str(e))

    return StreamingResponse(
        BytesIO(text2speech.generateAudioStream(
                Transcription(transcript.language_code, aiChatAnswer)
        )),
        media_type=os.getenv("APISERVICE_AUDIO_MIME_TYPE")
    )
