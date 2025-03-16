import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Enum, TIMESTAMP, text, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

# db.py があるディレクトリの絶対パスを取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DigiCertGlobalRootCA.crt を読み込むためのパスを組み立て
ssl_ca_path = os.path.join(BASE_DIR, "DigiCertGlobalRootCA.crt")

# SQLAlchemyの接続URLを作成
DATABASE_URL = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "ssl_ca": ssl_ca_path
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# userテーブル
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(Enum("male", "female", "other"), nullable=True)
    household = Column(Integer, nullable=True)
    time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=True)

class Reception(Base):
    __tablename__ = "reception"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    category_id = Column(Integer, nullable=True)
    time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"),nullable=True)

class Answer_info(Base):
    __tablename__ ="answer_info"
    id = Column(Integer, primary_key=True, autoincrement=True)
    reception_id = Column(Integer, nullable=False)
    question_id = Column(Integer, nullable=False)
    answer_numeric = Column(Integer, nullable=True)
    answer_categorical = Column(String(255), nullable=True)

