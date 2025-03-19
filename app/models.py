# app/models.py
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, text, ForeignKey
from sqlalchemy.types import Enum
from db import Base

# userテーブル
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(Enum("male", "female", "other"), nullable=True)
    household = Column(Integer, nullable=True)
    time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=True)

# receptionテーブル
class Reception(Base):
    __tablename__ = "reception"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    category_id = Column(Integer, nullable=True)
    time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"),nullable=True)

# answer_infoテーブル
class Answer_info(Base):
    __tablename__ ="answer_info"
    id = Column(Integer, primary_key=True, autoincrement=True)
    reception_id = Column(Integer, ForeignKey("reception.id"), nullable=False)
    question_id = Column(Integer, nullable=False)
    answer_numeric = Column(Integer, nullable=True)
    answer_categorical = Column(String(255), nullable=True)

