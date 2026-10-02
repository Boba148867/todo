from fastapi import APIRouter,Depends,Cookie,Query,HTTPException
from fastapi.responses import *
from models import *
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from auth import create_token,get_name

router=APIRouter()

@router.get('/')
async def mainpage():
    return Response(content='<h2>Здравствуйте! Введите в строке reg или login</h2>', media_type='text/html')

@router.post('/reg')
async def register(name=Query(), password=Query(), db:AsyncSession=Depends(get_db)):
    result=(await db.execute(select(User).filter(User.name==name))).first()
    if result:
        raise HTTPException(400,'Такой пользователь уже есть')
    target=User(name=name, password=password)
    db.add(target)
    await db.commit()

@router.post('/login')
async def login(name=Query(), password=Query(), db:AsyncSession=Depends(get_db)):
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
async def mainpag(token=Cookie()):
    return Response('<h2>Для добавления задачи ведите /add?name=...<br>Для просмотра введите /list</h2>', media_type='text/html')

@router.post('/add')
async def add(token=Cookie(), db:AsyncSession=Depends(get_db), name=Query()):
    result=(await db.execute(select(User).filter(User.name==get_name(token)))).first()
    if not(result):
        raise HTTPException(400,'Такого пользователя нет!')
    user=result[0]
    target=Task(title=name,user_id=user.id )
    db.add(target)
    await db.commit()

@router.get('/list')
async def listSHOW(token=Cookie(), db:AsyncSession=Depends(get_db)):
    result=(await db.execute(select(User).filter(User.name==get_name(token)).options(selectinload(User.tasks)))).first()
    if not(result):
        raise HTTPException(400,'Такого пользователя нет!')
    user=result[0]
    txt=''
    for i in user.tasks:
        txt+=f'<br>{i.title}<br>'
    return Response(txt, media_type='text/html')

@router.delete('/delete')
async def delet(name=Query(), token=Cookie(), db:AsyncSession=Depends(get_db)):
    result=(await db.execute(select(User).filter(User.name==get_name(token)).options(selectinload(User.tasks)))).first()
    if not(result):
        raise HTTPException(400,'Такого пользователя нет!')
    user=result[0]
    for i in user.tasks:
        if i.title==name:
            await db.delete(i)
            await db.commit()
            return {'status':'success'}