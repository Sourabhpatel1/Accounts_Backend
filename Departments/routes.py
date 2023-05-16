from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import ValidationError
from database import get_session
from .models import Departments, DepartmentBase
from .crud import create_department

dep_router = APIRouter(prefix="/department", tags=["Departments"])

@dep_router.get("/")
def read_all_departmens(session:Session=Depends(get_session)):
    departments = session.exec(select(Departments)).all()
    return departments

@dep_router.get("/{id}")
def read_department_by_id(id:int, session:Session=Depends(get_session)):
    department = session.get(Departments, id)
    if not department:
        raise HTTPException(status_code=404, detail=f"Department with id {id} does not exist.")
    return department

@dep_router.post("/")
def add_department(department:DepartmentBase, session:Session=Depends(get_session)):
    try:
        new_department = create_department(department=department, session=session)
        session.add(new_department)
        session.commit()
        session.refresh(new_department)
        return new_department
    except Exception as e:
        if isinstance(e, ValidationError):
            raise HTTPException(status_code=403,detail="If the department is a cost center then type of cost must be specified.")
        raise HTTPException(status_code=403, detail=str(e))
