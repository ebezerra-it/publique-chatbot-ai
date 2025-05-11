from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from pydantic import BaseModel
from ApiServices.Routes.Auth.authRoutes import authRouter
from ApiServices.Routes.ChatBot.chatbotRoutes import chatbothRouter
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="ApiServices/static"), name="static")
templates = Jinja2Templates(directory="ApiServices/templates")

app.include_router(
    authRouter, 
    prefix='/auth'
)

app.include_router(
    chatbothRouter,
    prefix="/bot"
)

@app.get("/")
def init_chatbot(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context= {
            "user_firstname": '',
            "publique_name": str(os.getenv("PUBLIQUE_NAME"))
        }
    )