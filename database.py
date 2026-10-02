from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
import os
from sqlalchemy.orm import sessionmaker
import aiosqlite

url=os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///tasks.db')
engine=create_async_engine(url)
SessionLocal=sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()