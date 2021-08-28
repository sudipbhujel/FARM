import ast
from typing import List, Optional

from app import crud
from app.models.student import Student, StudentInDB, StudentOut, UpdateStudent
from fastapi import APIRouter, Body, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
from pymongo.errors import WriteError

router = APIRouter()


async def common_parameters(
    sort: str = "['updated_at', 'DESC']",
    range: str = "[0, 24]",
    filter: Optional[str] = None
) -> dict:
    common = {"sort": eval(sort), "range": eval(range)}
    if filter is not None:
        common["filter"] = ast.literal_eval(filter)
    else:
        common["filter"] = filter
    return common


@router.post("/", response_description="Add new student", response_model=Student, status_code=201)
async def create_student(student: StudentInDB = Body(...)):
    student = jsonable_encoder(student)
    try:
        new_student = await crud.student.create(student)
    except WriteError as err:
        print(err)
        raise HTTPException(status_code=400, detail="Error")
    created_student = await crud.student.get(new_student.inserted_id)
    return created_student


@router.get(
    "/", response_description="List all students", response_model=List[StudentOut]
)
async def list_students(response: Response, commons: dict = Depends(common_parameters)):
    students = await crud.student.get_multi(commons)
    response.headers["Content-Range"] = f"students {commons['range'][0]}-{commons['range'][1] if commons['range'][1] < students['total'] else students['total'] }/{students['total']}"
    return students["data"]


@router.get(
    "/{id}", response_description="Get a single student", response_model=Student
)
async def show_student(id: str):
    if (student := await crud.student.get(id)) is not None:
        return student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


@router.put("/{id}", response_description="Update a student", response_model=UpdateStudent)
async def update_student(id: str, student: UpdateStudent = Body(...)):
    student = {k: v for k, v in student.dict().items() if v is not None}

    if len(student) >= 1:
        update_result = await crud.student.update(id, student)

        if update_result.modified_count == 1:
            if (
                updated_student := await crud.student.get(id)
            ) is not None:
                return updated_student

    if (existing_student := await crud.student.get(id)) is not None:
        return existing_student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


@router.delete("/{id}", response_description="Delete a student")
async def delete_student(id: str):
    delete_result = await crud.student.delete(id)

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Student {id} not found")
