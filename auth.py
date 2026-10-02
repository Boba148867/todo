from jose import jwt
from datetime import datetime,timedelta
from fastapi import HTTPException
SECRET='boba'
ALGORITHM='HS256'

def create_token(username:str):
    payload={'sub':username, 'exp':datetime.now()+timedelta(hours=1)}
    return jwt.encode(payload,SECRET,ALGORITHM)

def get_name(token:str):
    try:
        data=jwt.decode(token,SECRET,ALGORITHM)
        return data['sub']
    except:
        raise HTTPEexception(401, 'Проблема с токеном')
    