from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Login(BaseModel):
    login: str


class Signup(Login):
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class Signin(Login):
    password: Optional[str] = None
    oauth_access_token: Optional[str] = None
    oauth_provider: Optional[str] = None


class SignupResponse(Login):
    id: UUID
    first_name: Optional[str]
    last_name: Optional[str]

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class HistoryResponse(BaseModel):
    user_id: UUID
    login_time: datetime


class RoleResponse(BaseModel):
    name: str


class UserWithRolesResponse(Login):
    first_name: Optional[str]
    last_name: Optional[str]
    roles: list[RoleResponse]


class SigninResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserWithRolesResponse
