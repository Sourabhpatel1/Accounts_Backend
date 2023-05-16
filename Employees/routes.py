from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, Session, select
from database import get_session
from .models import Employees, EmployeesBase,  SalaryStructure, SalaryStructureBase
from .crud import create_employees, create_salary_structure

emp_router = APIRouter(prefix="/emp", tags=["Emplyees"])
 
@emp_router.get("/")
def read_all_employees(session:Session=Depends(get_session)):
    employees = session.exec(select(Employees)).all()
    return employees

@emp_router.get("/{id}")
def read_employee_by_id(id:int ,session:Session=Depends(get_session)):
    employee = session.get(Employees, id)
    if not employee:
        raise HTTPException(
            status_code=404, detail=f"Employee with id {id} does not exist."
        )
    return employee

@emp_router.get("/salary_structure")
def read_all_salary_structures(session:Session=Depends(get_session)):
    structures = session.exec(select(SalaryStructure)).all()
    return structures

@emp_router.get("/salary_strucure/{id}")
def read_salary_structure_by_id(id:int, session:Session=Depends(get_session)):
    structure = session.get(SalaryStructure, id)
    if not structure:
        raise HTTPException(
            status_code=404, detail=f"Salary structure with id {id} does not exist."
        )
    return structure

@emp_router.post("/")
def add_new_employee(employee:EmployeesBase, session:Session=Depends(get_session)):
    try:
        new_employee = create_employees(employee=employee, session=session)
        session.add(new_employee)
        session.commit()
        session.refresh(new_employee)
        return new_employee
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

@emp_router.post("/salary_strucure")
def add_new_salary_structure(salary:SalaryStructureBase, session:Session=Depends(get_session)):
    try:
        new_salary_structure = create_salary_structure(salary=salary)
        session.add(new_salary_structure)
        session.commit()
        session.refresh(new_salary_structure)
        return new_salary_structure
    except Exception as e:
        raise HTTPException(
            status_code=403, detail=str(e)
        )