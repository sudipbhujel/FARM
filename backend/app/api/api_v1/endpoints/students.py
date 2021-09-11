import ast
from typing import List, Optional

from app import crud
from app.models.student import Student, StudentInCreate, StudentInDB, StudentInResponse, StudentInUpdate
from fastapi import APIRouter, Body, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
from pymongo.errors import WriteError

from app.db.mongodb import AsyncIOMotorClient, get_database

router = APIRouter()


async def common_parameters(
    sort: str = "['updated_at', 'DESC']",
    range: str = "[0, 24]",
    filter: Optional[str] = None,
) -> dict:
    common = {"sort": eval(sort), "range": eval(range)}
    if filter is not None:
        common["filter"] = ast.literal_eval(filter)
    else:
        common["filter"] = filter
    return common


@router.post("/", response_description="Add new student", response_model=StudentInResponse, status_code=201)
async def create_student(
        student: StudentInCreate = Body(...), db: AsyncIOMotorClient = Depends(get_database)
) -> StudentInDB:
    student = jsonable_encoder(student)
    try:
        new_student = await crud.student.create(db, student)
    except WriteError as err:
        print(err)
        raise HTTPException(status_code=400, detail="Error")
    created_student = await crud.student.get_by_id(db, new_student.inserted_id)
    return created_student


@router.get(
    "/", response_description="List all students", response_model=List[StudentInResponse]
)
async def list_students(
        response: Response,
        commons: dict = Depends(common_parameters),
        db: AsyncIOMotorClient = Depends(get_database)):
    students = await crud.student.get_multi(db, commons)
    response.headers["Content-Range"] = f"students {commons['range'][0]}-{commons['range'][1] if commons['range'][1] < students['total'] else students['total'] }/{students['total']}"
    return students["data"]


@router.get(
    "/{id}", response_description="Get a single student", response_model=Student
)
async def show_student(id: str, db: AsyncIOMotorClient = Depends(get_database)):
    return await crud.student.get_student_or_404(db, id)


@router.put("/{id}", response_description="Update a student", response_model=StudentInResponse)
async def update_student(id: str, student: StudentInUpdate = Body(...), db: AsyncIOMotorClient = Depends(get_database)):
    student = {k: v for k, v in student.dict().items() if v is not None}

    if len(student) >= 1:
        update_result = await crud.student.update_by_id(db, id, student)

        if update_result.modified_count == 1:
            if (
                updated_student := await crud.student.get_by_id(db, id)
            ) is not None:
                return updated_student

    if (existing_student := await crud.student.get_by_id(db, id)) is not None:
        return existing_student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


@router.delete("/{id}", response_description="Delete a student")
async def delete_student(id: str, db: AsyncIOMotorClient = Depends(get_database)):
    delete_result = await crud.student.delete(db, id)

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Student {id} not found")
