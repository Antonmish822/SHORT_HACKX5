# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
import json

from database import SessionLocal, engine
from models import User, Quest, QuestSubmission
from schemas import (
    UserCreate, UserLogin, Token, UserProfile,
    QuestOut, QuestSubmissionBase, QuestSubmissionOut, QuestBase
)
from auth import (
    verify_password, get_password_hash,
    create_access_token, SECRET_KEY, ALGORITHM
)
from jose import jwt, JWTError

# Создаём таблицы при запуске
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Wall API — X5 Tech",
    description="API для регистрации, авторизации и учёта прогресса на умной стене",
    version="1.0.0"
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === Аутентификация ===

@app.post("/auth/register", response_model=Token, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Проверка уникальности contact
    db_user = db.query(User).filter(User.contact == user.contact).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким контактом уже существует")

    # Хешируем пароль, если указан
    hashed_pw = get_password_hash(user.password) if user.password else None

    db_user = User(
        contact=user.contact,
        hashed_password=hashed_pw,
        consent_given=user.consent_given,
        points=0,
        level="Новичок"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.contact == user.contact).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Неверный контакт или пароль")

    # Если пароль требуется (не Telegram-вход)
    if db_user.hashed_password:
        if not user.password or not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=400, detail="Неверный контакт или пароль")
    # Для Telegram: достаточно совпадения contact (в реальности — проверка через Bot API)

    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="auth/login")),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


# === Профиль и статистика ===

@app.get("/me", response_model=UserProfile)
def read_users_me(current_user: User = Depends(get_current_user)):
    completed = len(current_user.submissions)
    return {
        "id": current_user.id,
        "contact": current_user.contact,
        "points": current_user.points,
        "level": current_user.level,
        "interests": current_user.interests,
        "completed_quests": completed
    }


@app.put("/me/interests")
def update_interests(
    interests: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.interests = interests
    db.commit()
    return {"status": "ok"}


# === Задания (quests) ===

@app.get("/quests/", response_model=List[QuestOut])
def get_quests(db: Session = Depends(get_db)):
    return db.query(Quest).all()


@app.post("/quests/{quest_id}/submit", response_model=QuestSubmissionOut)
def submit_quest(
    quest_id: int,
    submission: QuestSubmissionBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    quest = db.query(Quest).filter(Quest.id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Задание не найдено")

    # Проверка, не выполнял ли уже
    existing = db.query(QuestSubmission).filter(
        QuestSubmission.user_id == current_user.id,
        QuestSubmission.quest_id == quest_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Задание уже выполнено")

    # Начисляем баллы
    current_user.points += quest.reward_points

    # Обновляем уровень (упрощённо)
    if current_user.points >= 200:
        current_user.level = "Гуру"
    elif current_user.points >= 100:
        current_user.level = "Эксперт"

    # Создаём запись
    new_sub = QuestSubmission(
        user_id=current_user.id,
        quest_id=quest_id,
        status=submission.status,
        metadata_json=submission.metadata_json
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)

    return new_sub


# === Админка (для менеджеров X5 Tech) ===

@app.post("/admin/quests", response_model=QuestOut, status_code=201)
def create_quest(
    quest: QuestBase,
    db: Session = Depends(get_db)
):
    db_quest = Quest(**quest.dict())
    db.add(db_quest)
    db.commit()
    db.refresh(db_quest)
    return db_quest

# Запуск: uvicorn main:app --reload --port 8000