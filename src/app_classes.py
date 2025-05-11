from Context.contextPublique import ContextPublique
from Text2Speech.text2SpeechGoogleCloud import Text2SpeechGoogleCloud
from Text2Speech.text2SpeechBase import Transcription
from Speech2Text.speech2TextGoogleGemini import Speech2TextGoogleGemini
from AIChat.aiChatGoogleGemini import AIChatGoogleGemini
from ChatInterface.chatInterfaceTelegram import ChatInterfaceTelegram
import google.generativeai as genai # type: ignore
from dotenv import load_dotenv
import logging
import sys
import os


def main():
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
        filename='publique-chabot-ai.log',
        filemode='a',
        level=loglevel, 
        format='%(asctime)s - %(levelname)s - %(message)s')

    context = ContextPublique(os.getenv("PUBLIQUE_CONTEXT"))

    text2speech = Text2SpeechGoogleCloud()

    #with open('output.mp3', 'wb') as f:
    #    f.write(text2speech.generateAudioStream(Transcription('pt-br', 'Quem vai ver o Sônic no cinema semana que vem? Levanta a mão!')))
    
    #print("fim")
    #exit(1)

    genai.configure(api_key=os.getenv("GOOGLE_GEMINI_APIKEY"))
    model = genai.GenerativeModel(os.getenv("GOOGLE_GEMINI_MODEL"))
    
    speech2Text = Speech2TextGoogleGemini(genai, model)

    aichat = AIChatGoogleGemini(logging, genai, model, context)

    chatTelegram = ChatInterfaceTelegram(logging, aichat, speech2Text, text2speech, str(os.getenv("TELEGRAM_AUDIO_MIME_TYPE")))
    chatTelegram.startPolling()

if __name__ == "__main__":
    try:
        main()
    except:
        logging.fatal('Uncaught exception in main(): ' + str(sys.exc_info()[1]))