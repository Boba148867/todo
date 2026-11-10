from sqlalchemy import Column, String, Integer,ForeignKey,func,DateTime
from sqlalchemy.orm import DeclarativeBase,relationship

class Base(DeclarativeBase):pass

class User(Base):
    __tablename__='users'
    id=Column(Integer, primary_key=True)
    name=Column(String, nullable=False)
    password=Column(String)

    tasks=relationship('Task', back_populates='user')

class Task(Base):
    __tablename__='tasks'
    id=Column(Integer, primary_key=True)
    title=Column(String)
    created_at=Column(Datetime, default=func.now())
    user_id=Column(Integer, ForeignKey('users.id'))

    user=relationship('User',back_populates='tasks')
