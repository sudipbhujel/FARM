from typing import List, Optional
from app.models.dbmodel import DBModelMixin, DateTimeModelMixin
from app.models.rwmode import RWModel

from pydantic import Field


class RoleBase(RWModel):
    name: str = Field(...)
    permissions: List[str] = Field(...)

    class Config(RWModel.Config):
        schema_extra = {
            "example": {
                "name": "user",
                "permissions": []
            }
        }


class Role(DateTimeModelMixin, RoleBase):
    pass


class RoleInDB(DBModelMixin, Role):
    pass


class RoleInResponse(DBModelMixin, Role):
    pass


class RoleInCreate(RoleBase):
    pass


class RoleInUpdate(RWModel):
    name: Optional[str]
    permissions: Optional[List[str]]

    class Config(RWModel.Config):
        schema_extra = {
            "example": {
                "name": "user",
                "permissions": []
            }
        }
