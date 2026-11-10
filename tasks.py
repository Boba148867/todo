from fastapi import APIRouter,Depends,Cookie,Query,HTTPException,Form,Body
from fastapi.responses import Response,FileResponse, RedirectResponse
from models import *
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,text
from sqlalchemy.orm import selectinload
from auth import create_token,get_name
from datetime import datetime

router=APIRouter()

@router.get('/')
async def log():
    return FileResponse('login.html')

@router.get('/register')
async def register():
    return FileResponse('register.html')
    
@router.post('/reg')
async def register(name=Form(), password=Form(), db:AsyncSession=Depends(get_db)):
    result=(await db.execute(select(User).filter(User.name==name))).first()
    if result:
        raise HTTPException(400,'Такой пользователь уже есть')
    target=User(name=name, password=password)
    db.add(target)
    await db.commit()
    return RedirectResponse('/', status_code=303)

@router.post('/login')
async def login(name=Form(), password=Form(), db:AsyncSession=Depends(get_db)):
    result=(await db.execute(select(User).filter(User.name==name))).first()
    if not(result):
        raise HTTPException(400,'Такого пользователя нет!')
    user=result[0]
    if user.password!=password:
        raise HTTPException(401,'Неправильный пароль или логин')
    token=create_token(user.name)
    response=RedirectResponse('/mainpage',status_code=303)
    response.set_cookie('token', token, max_age=3600, path='/')
    return response

@router.get('/mainpage')
async def mainpage(token=Cookie()):
    return FileResponse('mainpage.html')

@router.post('/add')
async def add(token=Cookie(), db:AsyncSession=Depends(get_db), data=Body()):
    result=(await db.execute(select(User).filter(User.name==get_name(token)))).first()
    if not(result):
        raise HTTPException(400,'Такого пользователя нет!')
    user=result[0]
    target=Task(title=data['task'],user_id=user.id, created_at=datetime.now().strftime('%Y-%M-%d'))
    db.add(target)
    await db.commit()
    await db.refresh(target)
    return {'id':target.id,'title':target.title}

@router.get('/tasks')
async def listSHOW(token=Cookie(), db:AsyncSession=Depends(get_db)):
    result=(await db.execute(select(User).filter(User.name==get_name(token)).options(selectinload(User.tasks)))).first()
    if not(result):
        raise HTTPException(400,'Такого пользователя нет!')
    user=result[0]
    txt=[]
    for i in user.tasks:
        txt.append({'id':i.id, 'text':i.title})
    return txt

@router.delete('/delete/{id}')
async def delet(id:int, token=Cookie(), db:AsyncSession=Depends(get_db)):
    result=(await db.execute(select(User).filter(User.name==get_name(token)).options(selectinload(User.tasks)))).first()
    if not(result):
        raise HTTPException(400,'Такого пользователя нет!')
    user=result[0]
    for i in user.tasks:
        if i.id==id:
            await db.delete(i)
            await db.commit()
            return RedirectResponse('/mainpage',status_code=303)

@router.get('/statistics')
async def get_stats(token=Cookie(), db:AyncSession=Depends(get_db)):
    result=(await db.execute(select(User).filter(User.name==get_name(token)).options(selectinload(User.tasks)))).first()
    if not(result):
        raise HTTPException(400,'Такого пользователя нет!')
    user=result[0]
    data=await db.execute(text(f'''
    SELECT COUNT(*), created_at from tasks
    GROUP BY created_at
    ''')).all()
    stats={}
    for i in data:
        stats.update({i[1]:i[0]})
    return stats
