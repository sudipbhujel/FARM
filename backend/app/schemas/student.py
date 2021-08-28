from typing import Optional
from bson import ObjectId

from pydantic import BaseModel
from pydantic import EmailStr


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# Shared properties
class StudentBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    course: Optional[str] = None
    gpa: Optional[float] = None


# Properties to receive on student creation
class StudentCreate(StudentBase):
    email: EmailStr
    gpa: float


# Properties to receive on student update
class StudentUpdate(StudentBase):
    pass


# Properties shared by models stored in DB
class StudentInDBBase(StudentBase):
    _id: PyObjectId
    email: EmailStr
    gpa: float


# Properties to return to client
class Student(StudentInDBBase):
    pass


# Properties properties stored in DB
class StudentInDB(StudentInDBBase):
    pass
