from sqlalchemy import Column, Integer, String, TIMESTAMP
from app.db.database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "user_management"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    username = Column(String, nullable=False)
    role = Column(String)  # Admin / User
    last_login = Column(TIMESTAMP, server_default=func.now())



from sqlalchemy import Column, Integer, String, Boolean, Float, TIMESTAMP, ForeignKey

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_management.id"))
    filename = Column(String)
    classified_status = Column(Boolean, default=False)
    classified_class = Column(String)
    uploaded_time = Column(TIMESTAMP, server_default=func.now())
    status = Column(String)  # Queue / In progress / Classified
    confidence = Column(Float)
    token = Column(Float)
    cost = Column(Float)


class DocumentMeta(Base):
    __tablename__ = "document_meta"

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("documents.id"))
    court = Column(String)
    petitioners = Column(String)
    respondents = Column(String)
    folder_path = Column(String)


from sqlalchemy import JSON

class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user_management.id"))
    session_id = Column(String)
    content = Column(JSON)
    qtoken = Column(Float)
    atoken = Column(Float)
    cost = Column(Float)
    response_time = Column(Float)
