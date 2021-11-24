from model.User.User import userBase

import motor.motor_asyncio
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')

database = client.crmv2
MGDB = database.tb_user


