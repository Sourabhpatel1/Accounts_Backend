from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from Accounts.models import Accounts
    from Inventory.models import InventoryItems

class TaxesBase(SQLModel):
    rate:float = Field(unique=True, index=True)

class GstOutput(TaxesBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    name:str 
    account_id:int = Field(foreign_key='accounts.id')
    account:"Accounts" = Relationship(back_populates='gst_output')
    items:Optional[List["InventoryItems"]] = Relationship(back_populates='gst_output')

class IgstOutput(TaxesBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    name:str 
    account_id:int = Field(foreign_key='accounts.id')
    account:"Accounts" = Relationship(back_populates='igst_output')
    items:Optional[List["InventoryItems"]] = Relationship(back_populates='igst_output')

class GstInput(TaxesBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    name:str 
    account_id:int = Field(foreign_key='accounts.id')
    account:"Accounts" = Relationship(back_populates='gst_input')
    items:Optional[List["InventoryItems"]] = Relationship(back_populates='gst_input')

class IgstInput(TaxesBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    name:str 
    account_id:int = Field(foreign_key='accounts.id')
    account:"Accounts" = Relationship(back_populates='igst_input')
    items:Optional[List["InventoryItems"]] = Relationship(back_populates='igst_input')