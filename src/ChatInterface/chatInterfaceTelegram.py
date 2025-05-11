from ChatInterface.chatInterfaceBase import ChatInterfaceBase
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler
from io import BytesIO
import sys
import os

class ChatInterfaceTelegram(ChatInterfaceBase):

    application: Application


    async def handleText(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        msg = update.message.text.strip()
        responseMsg = self.apiSendTextMessage(msg)
        await self.sendTextMessage(update, responseMsg)


    async def handleVoice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message.voice.duration > int(os.getenv("USER_AUDIO_MAXIMUM_DURATION_SECONDS")):
            await self.sendTextMessage(
                update,
                self.userMessages.getUserMessage(
                    'ERROR_MAXIMUM_AUDIO_DURATION',
                    update.effective_user.language_code
                ).format(max_duration=os.getenv("USER_AUDIO_MAXIMUM_DURATION_SECONDS"))
            )
            return

        try:
            audioStream = BytesIO(await (await update.message.voice.get_file()).download_as_bytearray())
        except:
            self.logger.error('Unable to download voice message from Telegram server: ' + str(sys.exc_info()[1]))
        
        responseStream = self.apiSendVoiceMessage(
            audioStream, 
            'voice_telegram.ogg', 
            str(os.getenv("TELEGRAM_AUDIO_MIME_TYPE"))
        )

        await self.sendVoiceMessage(update, responseStream)


    async def handleStart(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_firstname = (update.effective_user.first_name or update.effective_user.user_name).strip()
        language_code = (update.effective_user.language_code).strip()
        
        msgWelcome = self.apiWelcome(
            userFirstname=user_firstname,
            languageCode=language_code
        )

        await self.sendTextMessage(update, msgWelcome)


    def __init__(self, logger, audioMimeType) -> None:
        super().__init__(logger, audioMimeType)

        try:
            self.application = Application.builder().token(str(os.getenv("TELEGRAM_BOT_TOKEN"))).build()
        except:
            self.logger.error('Unable to auth bot token on Telegram server: ' + str(sys.exc_info()[1]))

        self.application.add_handler(CommandHandler("start", self.handleStart))
        self.application.add_handler(MessageHandler(filters.VOICE, self.handleVoice))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handleText))


    async def sendTextMessage(self, msgObject, text, **kwargs) -> None:
        try:
            await msgObject.message.reply_html(text, **kwargs, reply_to_message_id=msgObject.message.message_id)
        except:
            self.logger.error('Unable to send text message to Telegram server: ' + str(sys.exc_info()[1]))


    async def sendVoiceMessage(self, msgObject: any, audioStream: any) -> None:
        try:
            await msgObject.message.reply_voice(voice=audioStream, reply_to_message_id=msgObject.message.message_id)
        except:
            self.logger.error('Unable to send voice message to Telegram server: ' + str(sys.exc_info()[1]))


    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.logger.error(f"Unable to poll messages from Telegram server: {context.error}")    


    def startPolling(self) -> None:
        self.logger.log(self.logger.WARN, 'Bot started polling')
        self.application.add_error_handler(self.error_handler)
        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES, 
            drop_pending_updates=True)
