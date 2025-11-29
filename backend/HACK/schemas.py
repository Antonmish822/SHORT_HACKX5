# schemas.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List

class UserBase(BaseModel):
    contact: str  # email или @username

    @validator("contact")
    def validate_contact(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Контакт не может быть пустым")
        if "@" in v and not ("@" in v and "." in v.split("@")[-1]):
            raise ValueError("Некорректный email")
        if v.startswith("@") and len(v) < 3:
            raise ValueError("Слишком короткий Telegram username")
        return v

class UserCreate(UserBase):
    password: Optional[str] = None  # необязательно для Telegram
    consent_given: bool

class UserLogin(UserBase):
    password: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class QuestBase(BaseModel):
    title: str
    description: Optional[str] = None
    reward_points: int
    quest_type: str

class QuestOut(QuestBase):
    id: int

    class Config:
        orm_mode = True

class QuestSubmissionBase(BaseModel):
    quest_id: int
    status: str = "completed"
    metadata_json: Optional[str] = None

class QuestSubmissionOut(QuestSubmissionBase):
    id: int
    user_id: int
    submitted_at: str

    class Config:
        orm_mode = True

class UserProfile(BaseModel):
    id: int
    contact: str
    points: int
    level: str
    interests: Optional[str] = None
    completed_quests: int

    class Config:
        orm_mode = True