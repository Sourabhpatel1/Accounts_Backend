from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from pydantic import validator
from email_validator import validate_email, EmailNotValidError
import re

if TYPE_CHECKING:
    from Accounts.models import Accounts
    from PurchaseDocs.models import PurchaseOrders, PurchaseInvoices, PurchaseReturnVouchers

class VendorsBase(SQLModel):
    name:str = Field(index=True, unique=True)
    gst:str
    phone:int
    email:str
    street_address:str
    city:str
    state:str
    country:str
    postal_code:int

class Vendors(VendorsBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    p_orders:Optional[List["PurchaseOrders"]] = Relationship(back_populates='vendor')
    p_invoices:Optional[List["PurchaseInvoices"]] = Relationship(back_populates='vendor')
    return_vouchers:Optional[List["PurchaseReturnVouchers"]] = Relationship(back_populates='vendor')
    account_id:int = Field(foreign_key='accounts.id')
    account:"Accounts" = Relationship(back_populates='vendors')
    
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