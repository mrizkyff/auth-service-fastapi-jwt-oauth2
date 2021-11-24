from config.database import MGDB
from model.User.User import userBase
from passlib.hash import bcrypt 


async def fetch_all_user():
    users = []
    cursor = MGDB.find({})
    async for user in cursor:
        users.append(userBase(**user))
    return users

async def fetch_user_by_email(email):
    users = []
    cursor = MGDB.find({"email":email})
    async for user in cursor:
        users.append(userBase(**user))
    return users

async def create_user(user):
    document = user
    result = await MGDB.insert_one(document)
    return document

async def verify_password(current, password):
    return bcrypt.verify(current, password)