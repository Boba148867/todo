from fastapi import FastAPI
from models import Base
from sqlalchemy import create_engine
from tasks import router
import os

engine=create_engine(os.getenv('DATABASE_URL','sqlite:///tasks.db')
app=FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(router)
