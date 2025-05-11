import sys
from Speech2Text.speech2TextBase import Speech2TextBase, Transcription
import json
import re
import os

def clean_json_string(json_string):
    pattern = r'^```json\s*(.*?)\s*```$'
    cleaned_string = re.sub(pattern, r'\1', json_string, flags=re.DOTALL)
    return cleaned_string.strip()

class Speech2TextGoogleGemini(Speech2TextBase):

    genai: any
    model: any

    def __init__(self, genai, model=None) -> None:
        super().__init__()
        
        self.genai = genai

        if not model:
            model = self.genai.GenerativeModel(os.getenv("GOOGLE_GEMINI_MODEL"))
        
        self.model = model

    def getTranscription(self, audioMimeType, audioStream=None, audioPathNameFile=None) -> Transcription:
        if not audioStream and not audioPathNameFile:
            raise SystemError('Missing audio stream and audio file path')

        if audioStream:
            try:
                audioFile = self.genai.upload_file(audioStream, mime_type=audioMimeType)
            except:
                raise SystemError('Unable to upload audio stream to Gemini Google server: ' + str(sys.exc_info()[1]))
        else:
            try:
                audioFile = self.genai.upload_file(path=audioPathNameFile, mime_type=audioMimeType)
            except:
                raise SystemError('Unable to upload audio filepath ' + audioPathNameFile + ' to Gemini Google server: ' + str(sys.exc_info()[1]))
        
        # TO DO: File count max tokens

        try:
            result = self.model.generate_content(
                [
                    audioFile, 
                    os.getenv("SPEECH_TO_TEXT_AI_COMMAND")
                ]
            )
        except:
            raise SystemError('Unable to get audio transcription from Gemini server: ' + str(sys.exc_info()[1]))

        try:
            self.genai.delete_file(audioFile)
        except:
            raise SystemError('Unable to delete audio file from Gemini server: ' + str(sys.exc_info()[1]))

        try:
            transcription = json.loads(clean_json_string(result.text))
        except:
            print(result)
            print(result.text)
            raise SystemError('Unable to parse json file transcription: ' + str(sys.exc_info()[1]))

        return Transcription(language_code=transcription['language_code'], text=transcription['transcription'])

    