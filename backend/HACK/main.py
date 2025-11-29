# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
import crud
import models
from database import SessionLocal, engine
from schemas import (
    UserCreate, UserLogin, Token, UserProfile,
    QuestOut, QuestSubmissionBase, QuestSubmissionOut, QuestBase
)
from auth import hash_password, verify_password, create_access_token, get_user_id_from_token

# Создаем таблицы
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Wall API — X5 Tech",
    description="API для регистрации, авторизации и учёта прогресса на умной стене",
    version="1.0.0"
)

# OAuth2 схема
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Dependency для БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency для получения текущего пользователя
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = get_user_id_from_token(token)
    if user_id is None:
        raise credentials_exception

    user = crud.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user


# === Аутентификация ===

@app.post("/auth/register", response_model=Token, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Проверяем согласие
    if not user_data.consent_given:
        raise HTTPException(
            status_code=400,
            detail="Необходимо дать согласие на обработку персональных данных"
        )

    # Проверяем уникальность контакта
    if crud.get_user_by_contact(db, user_data.contact):
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким контактом уже существует"
        )

    # Валидация типа пользователя и пароля
    is_telegram = user_data.contact.startswith("@")

    if not is_telegram and not user_data.password:
        raise HTTPException(
            status_code=400,
            detail="Для email-регистрации пароль обязателен"
        )

    if is_telegram and user_data.password:
        raise HTTPException(
            status_code=400,
            detail="Для Telegram-регистрации пароль не требуется"
        )

    # Создаем пользователя
    user = crud.create_user(db, user_data)

    # Создаем токен
    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_contact(db, user_data.contact)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Неверный контакт или пароль"
        )

    is_telegram = user_data.contact.startswith("@")

    if is_telegram:
        # Telegram вход - только проверка существования пользователя
        pass
    else:
        # Email вход - проверка пароля
        if not user.hashed_password:
            raise HTTPException(
                status_code=400,
                detail="Для этого пользователя не установлен пароль"
            )

        if not user_data.password or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=400,
                detail="Неверный пароль"
            )

    # Создаем токен
    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}


# === Профиль ===

@app.get("/me", response_model=UserProfile)
def get_my_profile(current_user: models.User = Depends(get_current_user)):
    completed_quests = len([s for s in current_user.submissions if s.status == "completed"])

    return UserProfile(
        id=current_user.id,
        contact=current_user.contact,
        points=current_user.points,
        level=current_user.level,
        interests=current_user.interests,
        completed_quests=completed_quests
    )


@app.put("/me/interests")
def update_my_interests(
        interests: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    current_user.interests = interests
    db.commit()
    return {"status": "ok"}


# === Задания ===

@app.get("/quests/", response_model=List[QuestOut])
def get_all_quests(db: Session = Depends(get_db)):
    return crud.get_all_quests(db)


@app.post("/quests/{quest_id}/submit", response_model=QuestSubmissionOut)
def submit_quest(
        quest_id: int,
        submission_data: QuestSubmissionBase,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Проверяем существование задания
    quest = crud.get_quest_by_id(db, quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Задание не найдено")

    # Проверяем, не выполнял ли пользователь уже это задание
    existing_submission = crud.get_user_quest_submission(db, current_user.id, quest_id)
    if existing_submission:
        raise HTTPException(status_code=400, detail="Задание уже выполнено")

    # Создаем submission и начисляем баллы
    submission = crud.create_quest_submission(
        db, current_user, quest, submission_data
    )

    return submission


# === Админка ===

@app.post("/admin/quests", response_model=QuestOut, status_code=201)
def create_new_quest(quest_data: QuestBase, db: Session = Depends(get_db)):
    return crud.create_quest(db, quest_data)


@app.get("/admin/users", response_model=List[UserProfile])
def get_all_users(db: Session = Depends(get_db)):
    users = crud.get_all_users(db)
    result = []

    for user in users:
        completed_quests = len([s for s in user.submissions if s.status == "completed"])
        result.append(UserProfile(
            id=user.id,
            contact=user.contact,
            points=user.points,
            level=user.level,
            interests=user.interests,
            completed_quests=completed_quests
        ))

    return result


# Корневой endpoint
@app.get("/")
def root():
    return {
        "message": "Smart Wall API — X5 Tech",
        "version": "1.0.0",
        "docs": "/docs"
    }