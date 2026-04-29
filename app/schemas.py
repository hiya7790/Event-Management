from pydantic import BaseModel, EmailStr
from typing import Optional, List
import datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    is_admin: bool = False

class UserResponse(UserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Event Schemas
class EventBase(BaseModel):
    title: str
    description: str
    date: datetime.datetime
    location: str

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int

    class Config:
        from_attributes = True

# Team Schemas
class TeamResponse(BaseModel):
    id: int
    code: str
    event_id: int

    class Config:
        from_attributes = True

# Registration Schemas
class RegistrationCreate(BaseModel):
    team_code: Optional[str] = None

class RegistrationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    team_id: Optional[int] = None
    attended: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class RegistrationDetailResponse(RegistrationResponse):
    user: UserResponse
    event: EventResponse
    team: Optional[TeamResponse] = None

    class Config:
        from_attributes = True
