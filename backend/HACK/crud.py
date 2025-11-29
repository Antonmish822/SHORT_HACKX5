# crud.py
from sqlalchemy.orm import Session
import models
import schemas
from auth import hash_password


def get_user_by_contact(db: Session, contact: str):
    return db.query(models.User).filter(models.User.contact == contact).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user_data: schemas.UserCreate):
    hashed_password = hash_password(user_data.password) if user_data.password else None

    db_user = models.User(
        contact=user_data.contact,
        hashed_password=hashed_password,
        consent_given=user_data.consent_given,
        points=0,
        level="Новичок"
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_quests(db: Session):
    return db.query(models.Quest).all()


def get_quest_by_id(db: Session, quest_id: int):
    return db.query(models.Quest).filter(models.Quest.id == quest_id).first()


def get_user_quest_submission(db: Session, user_id: int, quest_id: int):
    return db.query(models.QuestSubmission).filter(
        models.QuestSubmission.user_id == user_id,
        models.QuestSubmission.quest_id == quest_id
    ).first()


def create_quest_submission(db: Session, user: models.User, quest: models.Quest,
                            submission_data: schemas.QuestSubmissionBase):
    # Начисляем баллы
    user.points += quest.reward_points

    # Обновляем уровень
    if user.points >= 200:
        user.level = "Гуру"
    elif user.points >= 100:
        user.level = "Эксперт"

    # Создаем submission
    submission = models.QuestSubmission(
        user_id=user.id,
        quest_id=quest.id,
        status=submission_data.status,
        metadata_json=submission_data.metadata_json
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def create_quest(db: Session, quest_data: schemas.QuestBase):
    db_quest = models.Quest(**quest_data.dict())
    db.add(db_quest)
    db.commit()
    db.refresh(db_quest)
    return db_quest


def get_all_users(db: Session):
    return db.query(models.User).all()