from abc import ABC, abstractmethod

class Transcription:
    language_code: str
    text: str

    def __init__(self, language_code, text) -> None:
        self.language_code = language_code
        self.text = text


class Speech2TextBase(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def getTranscription(self, audioMimeType, audioStream=None, audioPathName=None) -> Transcription:
        ...
    