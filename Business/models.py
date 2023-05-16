from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field
from pydantic import validator
from email_validator import validate_email, EmailNotValidError
import re

class BusinessBase(SQLModel):
    name:str = Field(index=True, unique=True)
    gst:str
    phone:int
    email:str
    street_address:str
    city:str
    state:str
    country:str
    postal_code:int
    fy_start : str
    fy_end : str
    next_year : bool

class Business(BusinessBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    is_active:bool = False
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 2:
            raise ValueError("Name must be atleast 2 characters long")
        return v
        
    @validator('email')
    def verify_email(cls, v):
        try:
            validate_email(v)
            return v
        except EmailNotValidError:
            raise ValueError("Please provide a valid email.")
    
    @validator('phone')
    def check_phone(cls, v):
        if len(str(v)) < 10:
            raise ValueError("Phone number must be atleast 10 digits.")
        return v

    @validator('gst')
    def check_gst(cls, v):
        regex = "/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/"
        validation = re.fullmatch(regex, v)
        if not validation or len(v) < 15:
            if v != "N/A":
                raise ValueError("Please enter a valid gst number.")
        return v