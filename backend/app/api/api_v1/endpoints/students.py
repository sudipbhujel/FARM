from typing import List

from app.db.db import db
from app.models.student import Student
from fastapi import APIRouter, Body, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pymongo.errors import WriteError

router = APIRouter()


@router.post("/", response_description="Add new student", response_model=Student)
async def create_student(student: Student = Body(...)):
    student = jsonable_encoder(student)
    try:
        new_student = await db["students"].insert_one(student)
    except WriteError as err:
        print(err)
        raise HTTPException(status_code=400, detail="Error")
    created_student = await db["students"].find_one({"_id": new_student.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_student)


@router.get(
    "/", response_description="List all students", response_model=List[Student]
)
async def list_students():
    students = await db["students"].find().to_list(1000)
    return students


@router.get(
    "/{id}", response_description="Get a single student", response_model=Student
)
async def show_student(id: str):
    if (student := await db["students"].find_one({"_id": id})) is not None:
        return student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


@router.put("/{id}", response_description="Update a student", response_model=Student)
async def update_student(id: str, student: Student = Body(...)):
    student = {k: v for k, v in student.dict().items() if v is not None}

    if len(student) >= 1:
        update_result = await db["students"].update_one({"_id": id}, {"$set": student})

        if update_result.modified_count == 1:
            if (
                updated_student := await db["students"].find_one({"_id": id})
            ) is not None:
                return updated_student

    if (existing_student := await db["students"].find_one({"_id": id})) is not None:
        return existing_student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


@router.delete("/{id}", response_description="Delete a student")
async def delete_student(id: str):
    delete_result = await db["students"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Student {id} not found")
