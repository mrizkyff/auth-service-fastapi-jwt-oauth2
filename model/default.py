from pydantic import BaseModel
from model.util import ObjectIdStr

class JwtToken(BaseModel):
    name: str = None
    schoolId : ObjectIdStr = None
    branchId : ObjectIdStr = None
    roles : str = None
    bankId : ObjectIdStr = None 