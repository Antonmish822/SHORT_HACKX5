# schemas.py
from pydantic import BaseModel, validator
from typing import Optional, List


class UserBase(BaseModel):
    contact: str

    @validator("contact")
    def validate_contact(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Контакт не может быть пустым")

        if "@" in v and not v.startswith("@"):
            parts = v.split("@")
            if len(parts) != 2 or not parts[0] or "." not in parts[1]:
                raise ValueError("Некорректный email")
        elif v.startswith("@") and len(v) < 2:
            raise ValueError("Слишком короткий Telegram username")
        elif not v.startswith("@") and "@" not in v:
            raise ValueError("Контакт должен быть email или Telegram username (начинается с @)")

        return v


class UserCreate(UserBase):
    password: Optional[str] = None
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