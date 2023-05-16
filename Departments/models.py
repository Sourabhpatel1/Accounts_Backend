from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from pydantic import validator, root_validator, ValidationError

if TYPE_CHECKING:
    from Employees.models import Employees

class CostType(Enum):
    Direct:str = "d"
    Indirect:str = 'i'

class DepartmentBase(SQLModel):
    name:str = Field(unique=True, index=True)
    is_cost_center:bool = Field(default=False)
    type_of_cost:Optional[CostType] = Field(default=None)


class Departments(DepartmentBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    employees:Optional[List["Employees"]] = Relationship(back_populates='department')

    @root_validator()
    def validate_cost_center(cls, values):
        if not values.get("is_cost_center"):
            values["type_of_cost"] = None

        if values.get("is_cost_center"):
            if not values.get("type_of_cost"):
                raise ValueError()

        return values
        

