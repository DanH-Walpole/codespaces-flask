import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Database connection
DB_URL = os.environ.get('DATABASE_URL', 'sqlite:///flaskapp.db')
engine = create_engine(DB_URL)
Base = declarative_base()

# Define models
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # In production, store only password hashes
    messages = relationship('Message', back_populates='user')

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='messages')

# Create the tables
def init_db():
    Base.metadata.create_all(engine)
    print("Database tables created!")

if __name__ == '__main__':
    init_db()