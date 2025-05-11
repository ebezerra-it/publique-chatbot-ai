from datetime import datetime, timedelta
import hashlib
from typing import Union, Annotated
from fastapi.security import HTTPBearer

auth_scheme = HTTPBearer()

db_users=[
    { 'username': 'edubbulhoes', 'encrypted_password': hashlib.sha256('123qwe'.encode("utf-8")).hexdigest(), 'access_token': '', 'token_expires': None },
    { 'username': 'lelemr', 'encrypted_password': hashlib.sha256('qwe123'.encode("utf-8")).hexdigest(), 'access_token': '', 'token_expires': None },
]

def authUser(username: str, password: str) -> Union[str, None]:
    user = next((user for user in db_users if user['username'] == username), None)

    if user:
        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if password_hash == user['encrypted_password']:
            token_expires = datetime.now() + timedelta(hours=8)
            access_token = hashlib.sha256((username + password + token_expires.isoformat()).encode("utf-8")).hexdigest()
            
            user['access_token'] = hashlib.sha256((username + password).encode("utf-8")).hexdigest()
            user['token_expires'] = token_expires
            return access_token
    
    return None

# def checkAuth(token: Annotated[str, auth_scheme]) -> bool:
def checkAuth(token: Annotated[str, auth_scheme]) -> bool:
    
    print(token)
    return True

    user = next((user for user in db_users if user['username'] == username), None)
    if user:
        if user['access_token'] == access_token:
            if datetime.now() < user['token_expires']:
                return True
    
    return False
            


