from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from Entries.models import DrEntries, CrEntries
    from Inventory.models import InventoryItems
    from Customers.models import Customers
    from Vendors.models import Vendors
    from Taxes.models import GstOutput, GstInput, IgstInput, IgstOutput
    
class PrimaryAccounts(SQLModel, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    name:str = Field(index=True, unique=True)
    group_accounts:List["GroupAccounts"] = Relationship(back_populates='primary_account')

class GroupAccountsBase(SQLModel):
    name:str = Field(index=True, unique=True)
    primary_account_id:int = Field(foreign_key='primaryaccounts.id')

class GroupAccounts(GroupAccountsBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    primary_account:"PrimaryAccounts" = Relationship(back_populates='group_accounts')
    sub_groups:List["SubGroups"] = Relationship(back_populates='group_account')

class SubGroupBase(SQLModel):
    name:str = Field(index=True, unique=True)
    group_account_id:int = Field(foreign_key='groupaccounts.id')

class SubGroups(SubGroupBase, table=True):
    id:int = Field(primary_key=True, index=True)
    group_account:GroupAccounts = Relationship(back_populates='sub_groups')
    accounts:Optional[List["Accounts"]] = Relationship(back_populates='sub_group')

class AccountsBase(SQLModel):
    name:str = Field(index=True, unique=True)
    sub_group_id:int = Field(foreign_key='subgroups.id')

class Accounts(AccountsBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    sub_group:"SubGroups" = Relationship(back_populates='accounts')
    dr_entries:Optional[List["DrEntries"]] = Relationship(back_populates='account')
    cr_entries:Optional[List["CrEntries"]] = Relationship(back_populates='account')
    inventory_items:Optional[List["InventoryItems"]] = Relationship(back_populates='inventory_account')
    customers:Optional[List["Customers"]] = Relationship(back_populates='account')
    vendors:Optional[List["Vendors"]] = Relationship(back_populates='account')
    gst_output:Optional["GstOutput"] = Relationship(back_populates='account')
    igst_output:Optional["IgstOutput"] = Relationship(back_populates='account')
    gst_input:Optional["GstInput"] = Relationship(back_populates='account')
    igst_input:Optional["IgstInput"] = Relationship(back_populates='account')
    