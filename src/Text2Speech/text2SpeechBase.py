from abc import ABC, abstractmethod
from typing_extensions import Buffer
from Speech2Text.speech2TextBase import Transcription


class Text2SpeechBase(ABC):
    def __init__(self, ) -> None:
        super().__init__()

    @abstractmethod
    def generateAudioStream(self, transcription: Transcription) -> Buffer:
        ...
    