import ast
from typing import List, Optional

from app import crud
from app.core.dependencies import PermissionChecker
from app.models.role import Role, RoleInCreate, RoleInDB, RoleInResponse, RoleInUpdate
from fastapi import APIRouter, Body, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
from pymongo.errors import WriteError

from app.db.mongodb import AsyncIOMotorClient, get_database

router = APIRouter()


allow_add_role = PermissionChecker("add_role")
allow_show_role = PermissionChecker("show_role")
allow_change_role = PermissionChecker("change_role")
allow_delete_role = PermissionChecker("delete_role")


async def common_parameters(
    sort: str = "['updated_at', 'DESC']",
    range: str = "[0, 24]",
    filter: Optional[str] = None,
) -> dict:
    common = {"sort": eval(sort), "range": eval(range)}
    common["filter"] = ast.literal_eval(
        filter) if filter is not None else filter
    return common


@router.post("/",
             response_description="Add new role",
             response_model=RoleInResponse,
             status_code=status.HTTP_201_CREATED,
             dependencies=[
                 Depends(allow_add_role)]
             )
async def create_role(
        role: RoleInCreate = Body(...), db: AsyncIOMotorClient = Depends(get_database)
) -> RoleInDB:
    role = jsonable_encoder(role)
    try:
        new_role = await crud.role.create(db, role)
    except WriteError as err:
        print(err)
        raise HTTPException(status_code=400, detail="Error")
    created_role = await crud.role.get_by_id(db, new_role.inserted_id)
    return created_role


@router.get(
    "/", response_description="List all roles",
    response_model=List[RoleInResponse],
    dependencies=[
        Depends(allow_show_role)]
)
async def list_roles(
        response: Response,
        commons: dict = Depends(common_parameters),
        db: AsyncIOMotorClient = Depends(get_database)):
    roles = await crud.role.get_multi(db, commons)
    response.headers["Content-Range"] = f"roles {commons['range'][0]}-{commons['range'][1] if commons['range'][1] < roles['total'] else roles['total'] }/{roles['total']}"
    return roles["data"]


@router.get(
    "/{id}", response_description="Get a single role",
    response_model=RoleInResponse,
    dependencies=[
        Depends(allow_add_role)]
)
async def show_role(id: str, db: AsyncIOMotorClient = Depends(get_database)):
    return await crud.role.get_role_or_404(db, id)


@router.put("/{id}",
            response_description="Update a role",
            response_model=RoleInResponse,
            dependencies=[
                Depends(allow_change_role)]
            )
async def update_role(id: str, role: RoleInUpdate = Body(...), db: AsyncIOMotorClient = Depends(get_database)):
    role = {k: v for k, v in role.dict().items() if v is not None}

    if len(role) >= 1:
        update_result = await crud.role.update_by_id(db, id, role)

        if update_result.modified_count == 1:
            if (
                updated_role := await crud.role.get_by_id(db, id)
            ) is not None:
                return updated_role

    if (existing_role := await crud.role.get_by_id(db, id)) is not None:
        return existing_role

    raise HTTPException(status_code=404, detail=f"Role {id} not found")


@router.delete("/{id}",
               response_description="Delete a role",
               dependencies=[Depends(allow_delete_role)]
               )
async def delete_role(id: str, db: AsyncIOMotorClient = Depends(get_database)):
    delete_result = await crud.role.delete(db, id)

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Role {id} not found")
