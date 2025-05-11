from fastapi import APIRouter
from typing import Annotated
from pydantic import BaseModel
from ..Auth import auth

authRouter = APIRouter()

class LoginData(BaseModel):
    username: str
    password: str


@authRouter.post("/signin")
async def signin(loginData: LoginData):
    access_token = auth.authUser(loginData.username, loginData.password)
    
    if access_token:
        return {
            "status": "ok",
            "message": "login successful",
            "access_token": access_token
        }
    
    return {
        "status": "error",
        "message": "login failed",
    }
 