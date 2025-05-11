from AIChat.aiChatBase import AIChatBase
from Context.contextBase import ContextBase
from io import BytesIO
from threading import Timer
import logging
import sys
import os


class AIChatGoogleGemini(AIChatBase):
    model: any
    genai: any
    contextFile: any
    context: ContextBase
    timer: Timer

    def __init__(self, logger: logging, genai, model, context: ContextBase) -> None:
        super().__init__(logger, context)
        
        self.genai = genai
        self.model = model
        self.contextFile = {}
        self.timer = None

        try:
            self.deleteAllGeminiContextFiles()
        except SystemError as e:
            self.stopUpdateContextTimer()
            self.logger.fatal(str(e))
            exit(1)
        
        self.updateContextData()

        # Check and upload context file regularly to have recent updated data
        if int(os.getenv("GOOGLE_GEMINI_CONTEXT_FILE_UPDATE_INTERVAL_SECONDS")) > 0:
            self.startUpdateContextTimer()
            self.logger.warn('Update Context File Timer started')

    
    def uploadContextFile(self) -> bool:
        if self.contextFile:
            try:
                self.genai.delete_file(self.contextFile)
            finally:
                pass

        try:
            self.contextFile = self.genai.upload_file(
                BytesIO(bytes(self.context.contextData.data, encoding='utf-8')), 
                display_name=str(os.getenv("PUBLIQUE_NAME")), 
                mime_type=str(os.getenv("CONTEXT_FILE_TYPE"))
            )
            return True
        except:
            self.logger.error('Unable to upload context file: ' + str(sys.exc_info()[1]))
            return False

    def updateContextData(self) -> bool:
        try:
            if super().updateContextData():
                return self.uploadContextFile()
        except ValueError as e:
            self.stopUpdateContextTimer()
            self.logger.fatal(str(e))
            exit(1)
        except:
            self.logger.error('Unable to update context file: ' + str(sys.exc_info()[1]))
            return False

        # file deleted by google server
        try:
            self.genai.get_file(name=self.contextFile.name)
        except:
            return self.uploadContextFile()
                
        return False


    def askAIChat(self, question, language_code='pt-br') -> str:
        try:
            result = self.model.generate_content(
                [
                    self.contextFile, 
                    os.getenv("AI_CHAT_COMMAND").format(publique_name=os.getenv("PUBLIQUE_NAME"),
                                                        language_code=language_code, 
                                                        question=question)
                ]
            )
        except:
            raise SystemError('Unable to ask to AI Google Gemini Chat: ' + str(sys.exc_info()[1]))

        return result.text
    
    def startUpdateContextTimer(self) -> None:
        self.timer = Timer(
            int(os.getenv("GOOGLE_GEMINI_CONTEXT_FILE_UPDATE_INTERVAL_SECONDS")), 
            self.updateContextTimerWorker)
        
        self.timer.start()

    def stopUpdateContextTimer(self) -> None:
        if self.timer:
            self.logger.warn('Update Context File Timer stopped')
            self.timer.cancel()
            self.timer = None

    def updateContextTimerWorker(self) -> None:
        if self.timer:
            self.startUpdateContextTimer()

        try:
            if self.updateContextData():
                self.logger.warn('Context File updated')
        except:
            try:
                self.genai.configure(api_key=os.getenv("GOOGLE_GEMINI_APIKEY"))
                self.model = self.genai.GenerativeModel(os.getenv("GOOGLE_GEMINI_MODEL"))
            except:
                self.logger.fatal('Unable to update Context File: ' + str(sys.exc_info()[1]))
                self.stopUpdateContextTimer()
                return

    def deleteAllGeminiContextFiles(self) -> None:
        count = 0

        try:
            myFiles = self.genai.list_files()
            for file in myFiles:
                self.genai.delete_file(file)
                count+=1

            self.logger.warn('Context files cleaned: ' + str(count))
        except:
            raise SystemError('Unable to delete old context files: ' + str(sys.exc_info()[1]))
