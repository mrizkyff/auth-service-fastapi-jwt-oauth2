from pydantic import BaseModel
from pydantic.fields import Field

from model.util import ObjectIdStr

class credentialIdBase(BaseModel):
    password : str = None
    roles : str = None

class addressBase(BaseModel):
    province : str = None
    city : str = None
    regency : str = None
    detail : str = None

class userBase(BaseModel):
    id : ObjectIdStr = Field(alias="_id")
    name: str = None
    css: str = None
    email: str = None
    schoolId : ObjectIdStr = None
    branchId : ObjectIdStr = None
    credentialId : credentialIdBase
    bankId : ObjectIdStr = None
    address : addressBase

