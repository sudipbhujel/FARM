from datetime import datetime, timezone
from typing import List, Optional
from app.models.dbmodel import DBModelMixin, DateTimeModelMixin
from app.models.rwmode import RWModel

from bson import ObjectId
from pydantic import EmailStr, Field


class StudentBase(RWModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    course: Optional[str] = Field(None)
    gpa: float = Field(..., le=4.0)

    class Config(RWModel.Config):
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": "3.0",
            }
        }


class Student(DateTimeModelMixin, StudentBase):
    pass


class StudentInDB(DBModelMixin, Student):
    pass


class StudentInResponse(DBModelMixin, Student):
    pass


class StudentInCreate(StudentBase):
    pass


class StudentInUpdate(RWModel):
    name: Optional[str]
    email: Optional[EmailStr]
    course: Optional[str]
    gpa: Optional[float]
    updated_at: Optional[datetime] = Field(None)

    class Config(RWModel.Config):
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": "3.0",
            }
        }
