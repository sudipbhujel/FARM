from typing import List

from app import crud
from app.models.student import Student, StudentInDB, UpdateStudent
from fastapi import APIRouter, Body, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from pymongo.errors import WriteError

router = APIRouter()


@router.post("/", response_description="Add new student", response_model=Student)
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
    "/", response_description="List all students", response_model=List[Student]
)
async def list_students(skip: int = 0, limit: int = 100):
    students = await crud.student.get_multi(skip, limit)
    return students


@router.get(
    "/{id}", response_description="Get a single student", response_model=Student
)
async def show_student(id: str):
    if (student := await crud.student.get(id)) is not None:
        return student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


@router.put("/{id}", response_description="Update a student", response_model=Student)
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
