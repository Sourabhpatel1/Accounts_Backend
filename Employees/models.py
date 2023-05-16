from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from Departments.models import Departments

class EmployeesBase(SQLModel):
    name:str = Field(index=True)
    age:int 
    positon:str
    street_address:str
    city:str
    state:str
    country:str
    postal_code:str 
    email:str 
    phone:int 
    department_id:int = Field(foreign_key='departments.id')
    salary_structure_id:Optional[int] = Field(foreign_key='salarystructure.id')

class Employees(EmployeesBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    department:"Departments" = Relationship(back_populates='employees')
    salary_structure:Optional["SalaryStructure"] = Relationship(back_populates='employees')

class SalaryStructureBase(SQLModel):
    name:str = Field(unique=True, index=True)
    basic_salary:float
    da_rate:Optional[float]
    hra:Optional[float]
    lta:Optional[float]
    conveyance_allowance:Optional[float]
    medical_allowance:Optional[float]
    overtime:Optional[float]
    pli:Optional[float]
    reimbursements:Optional[float]
    epf:Optional[float]
    esic:Optional[float]
    tds:Optional[float]

class SalaryStructure(SalaryStructureBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    employees:Optional[List["Employees"]] = Relationship(back_populates='salary_structure')