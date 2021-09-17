from datetime import timedelta

from app import crud
from app.core.config import settings
from app.core.dependencies import PermissionChecker
from app.core.jwt import (authenticate_user, create_access_token,
                          get_current_active_user)
from app.db.mongodb import AsyncIOMotorClient, get_database
from app.models.user import (Token, User, UserInCreate, UserInResponse,
                             UserInUpdate)
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.param_functions import Body
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


allow_add_user = PermissionChecker("add_user")
allow_show_user = PermissionChecker("show_user")
allow_change_user = PermissionChecker("change_user")
allow_delete_user = PermissionChecker("delete_user")


@router.post("/",
             response_description="Create a new user",
             response_model=User,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allow_add_user)]
             )
async def create_user(user: UserInCreate, db: AsyncIOMotorClient = Depends(get_database)):
    await crud.user.check_free_username_and_email(db, user.username)

    dbuser = await crud.user.create_user(db, user)
    return dbuser


@router.put("/{id}",
            response_description="Update a user",
            response_model=UserInResponse,
            dependencies=[
                Depends(allow_change_user)]
            )
async def update_user(id: str, user: UserInUpdate = Body(...), db: AsyncIOMotorClient = Depends(get_database)):
    user = {k: v for k, v in user.dict().items() if v is not None}

    if len(user) >= 1:
        update_result = await crud.user.update_by_id(db, id, user)

        if update_result.modified_count == 1:
            if (
                updated_user := await crud.user.get_by_id(db, id)
            ) is not None:
                return updated_user

    if (existing_user := await crud.user.get_by_id(db, id)) is not None:
        return existing_user

    raise HTTPException(status_code=404, detail=f"User {id} not found")


@router.post("/token", response_model=Token)
async def login_for_access_token(response: Response,
                                 form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: AsyncIOMotorClient = Depends(get_database)):
    user = await authenticate_user(
        db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response.set_cookie(key="auth", value=access_token, httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/register",
    response_model=UserInResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(response: Response, user: UserInCreate, db: AsyncIOMotorClient = Depends(get_database)):
    await crud.user.check_free_username_and_email(db, user.username)

    async with await db.start_session() as s:
        async with s.start_transaction():
            dbuser = await crud.user.create_user(db, user)

            access_token_expires = timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = await create_access_token(
                data={"sub": user.username}, expires_delta=access_token_expires
            )
            response.set_cookie(key="auth", value=access_token, httponly=True)
            token = {"access_token": access_token, "token_type": "bearer"}
            return UserInResponse(user=User(**dbuser.dict()), token=token)


@router.get("/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
