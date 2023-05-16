from sqlmodel import Session
from Departments.models import Departments
from .models import Employees, EmployeesBase, SalaryStructure, SalaryStructureBase

def create_employees(employee:EmployeesBase, session:Session):
    department = session.get(Departments, employee.department_id)
    
    if not department:
        raise ValueError(f"Department with id {employee.department_id} does not exists.")
    
    new_employee = Employees.from_orm(employee, update={
        'department' : department, 'department_id' : department.id
    })
    return new_employee

def create_salary_structure(salary:SalaryStructureBase):
    new_salary_structure = SalaryStructure.from_orm(salary)
    return new_salary_structure