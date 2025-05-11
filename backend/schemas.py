from pydantic import BaseModel

class LogCreate(BaseModel):
    UID: str
    Action: str
    Date: str
    Time: str

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
