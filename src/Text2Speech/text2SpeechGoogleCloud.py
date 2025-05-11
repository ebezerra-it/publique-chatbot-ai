from Text2Speech.text2SpeechBase import Text2SpeechBase, Transcription
from google.cloud import texttospeech # type: ignore
#import text2SpeechBase as texttospeech
from typing_extensions import Buffer
import sys
import os

class Text2SpeechGoogleCloud(Text2SpeechBase):
    def __init__(self) -> None:
        super().__init__()

    def generateAudioStream(self, transcription: Transcription) -> Buffer:
        
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                '../../',
                os.getenv("GOOGLE_CLOUD_CREDENTIALS_JSON_FILE")
        )

        try:
            client = texttospeech.TextToSpeechClient()
        except:
            raise SystemError('Unable to auth on Google Cloud server: ' + str(sys.exc_info()[1]))

        synthesis_input = texttospeech.SynthesisInput(text=transcription.text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=transcription.language_code, 
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            pitch=-10.0,
            #speaking_rate=0.85
        )

        try:
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
        except:
            raise SystemError('Unable generate synthetized speech on Google Cloud server: ' + str(sys.exc_info()[1]))

        return response.audio_content