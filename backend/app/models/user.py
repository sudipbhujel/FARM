from typing import Optional
from app.core.security import get_password_hash, verify_password
from app.models.dbmodel import DBModelMixin
from app.models.rwmode import RWModel

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(RWModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False


class UserInDB(DBModelMixin, UserBase):
    hashed_password: str = ""

    def check_password(self, password: str):
        return verify_password(password, self.hashed_password)

    def change_password(self, password: str):
        self.hashed_password = get_password_hash(password)


class User(UserBase):
    pass


class UserInResponse(RWModel):
    token: Token
    user: User


class UserInLogin(RWModel):
    username: str
    password: str


class UserInCreate(UserInLogin):
    pass


class UserInUpdate(RWModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
