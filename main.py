from fastapi import FastAPI
from datetime import timedelta, datetime
from fastapi import (
    Depends,
    HTTPException,
    status,
    Security
)
from fastapi.security import (
    OAuth2PasswordBearer, 
    OAuth2PasswordRequestForm,
    SecurityScopes,
    )
from function.user import fetch_user_by_email, fetch_all_user, verify_password
from model.User.User import userBase
import jwt

from model.default import JwtToken

app = FastAPI()

JWT_SECRET = "104923123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

# otentikasi dengan email dan password
async def authenticate_user_by_email(email:str, password: str):
    response = await fetch_user_by_email(email)
    if len(response) == 1:
        getPassword = response[0].credentialId.password
        return await verify_password(password, getPassword)

# cari user by email
async def get_user_by_email(email:str):
    response = await fetch_user_by_email(email)
    if len(response) == 1:
        return response
    return None

# membuat access token
async def create_access_token(data: JwtToken, expires_delta: int):
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=1)
    data.exp = expire
    encoded_jwt = jwt.encode(data.dict(), JWT_SECRET, ALGORITHM)

    return encoded_jwt

# token scheme
@app.post('/token')
async def generate_token(form_data : OAuth2PasswordRequestForm = Depends()):
    email = form_data.username
    password = form_data.password
    user = await authenticate_user_by_email(email, password)
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

    token = await create_access_token(data_token, ACCESS_TOKEN_EXPIRE_MINUTES)
    return {'access_token': token}

# ambil user sekarang
@app.get("/get_current_user", response_model=JwtToken)
async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    # define credential exception
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # decode token and extract username and expires data
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        # username: str = payload.get("sub")
        # expires = payload.get("exp")
        data_token = JwtToken()
        data_token.name = payload.get("name")
        data_token.schoolId = payload.get("schoolId")
        data_token.branchId = payload.get("branchId")
        data_token.roles = payload.get("roles")
        data_token.bankId = payload.get("bankId")
        data_token.exp = payload.get("exp")
    except jwt.PyJWTError:
        raise credentials_exception
    return data_token


# get semua user
@app.get("/get_all_users")
async def get_all_users(token: str = Depends(oauth2_scheme)):
    response = await fetch_all_user()
    if response:
        return response
    return {"result":"error guis"}

# get user by email
@app.get("/get_user_by_email")
async def get_user_by_email(email:str):
    response = await fetch_user_by_email(email)
    if len(response) == 1:
        return response
    return {"result":"error guis"}

# buat user
@app.post("create_user")
async def create_user(user: userBase):
    response = await create_user(user)
    if response:
        return response
    return {"error":response}