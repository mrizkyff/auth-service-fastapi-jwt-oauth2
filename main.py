from fastapi import FastAPI
from datetime import timedelta
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from function.user import fetch_user_by_email, fetch_all_user, verify_password
from model.User.User import userBase
import jwt

from model.default import JwtToken

app = FastAPI()

JWT_SECRET = "104923123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

async def authenticate_user_by_email(email:str, password: str):
    response = await fetch_user_by_email(email)
    if len(response) == 1:
        getPassword = response[0].credentialId.password
        if(verify_password(getPassword, password)):
            return True
    return False

async def get_user_by_email(email:str):
    response = await fetch_user_by_email(email)
    if len(response) == 1:
        return response
    return None
    

@app.post('/token')
async def generate_token(form_data : OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user_by_email(form_data.username, form_data.password)
    if not user:
        return {'error':'invalid credential'}
    
    user_obj = await get_user_by_email(form_data.username)
    user_obj = user_obj[0]

    data_token = JwtToken()
    data_token.name = user_obj.name
    data_token.schoolId = user_obj.schoolId
    data_token.branchId = user_obj.branchId
    data_token.roles = user_obj.credentialId.roles
    data_token.bankId = user_obj.bankId

    
    token = jwt.encode(data_token.dict(), JWT_SECRET, ALGORITHM)


    return {'access_token':token}


@app.get("/get_all_users")
async def get_all_users():
    response = await fetch_all_user()
    if response:
        return response
    return {"result":"error guis"}

@app.get("/get_user_by_email")
async def get_user_by_email(email:str):
    response = await fetch_user_by_email(email)
    if len(response) == 1:
        return response
    return {"result":"error guis"}

@app.post("create_user")
async def create_user(user: userBase):
    response = await create_user(user)
    if response:
        return response
    return {"error":response}