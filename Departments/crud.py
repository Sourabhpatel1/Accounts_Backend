from sqlmodel import Session
from .models import DepartmentBase, Departments

def create_department(department:DepartmentBase, session:Session):
    new_department = Departments.from_orm(department)
    return new_department

    
