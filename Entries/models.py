from typing import Optional, List, TYPE_CHECKING
from enum import Enum
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from Accounts.models import Accounts
    from Journals.models import Journals
    from SalesDocs.models import SalesInvoices, SalesReturnVouchers
    from PurchaseDocs.models import PurchaseInvoices, PurchaseReturnVouchers

class EntryType(Enum):
    Debit:str = "dr"
    Credit:str = "cr"

class EntriesRequest(SQLModel):
    account_id:int = Field(foreign_key='accounts.id')
    amount:float

class MasterEntryRequest(EntriesRequest):
    entry_type:EntryType

class EntriesBase(EntriesRequest):
    date_created:datetime = datetime.utcnow()

class EntryLink(SQLModel, table=True):
    dr_entry_id:Optional[int] = Field(default=None, foreign_key='drentries.id', primary_key=True)
    cr_entry_id:Optional[int] = Field(default=None, foreign_key='crentries.id', primary_key=True)

class DrEntries(EntriesBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    account:"Accounts" = Relationship(back_populates='dr_entries')
    journal_id:Optional[int] = Field(foreign_key='journals.id')
    sales_invoice_id:Optional[int] = Field(foreign_key='salesinvoices.id')
    purchase_invoice_id:Optional[int] = Field(foreign_key='purchaseinvoices.id')
    purchase_return_voucher_id:Optional[int] = Field(foreign_key='purchasereturnvouchers.id')
    sales_return_voucher_id:Optional[int] = Field(foreign_key='salesreturnvouchers.id')
    journal:Optional["Journals"] = Relationship(back_populates='dr_entries')
    sales_invoice:Optional["SalesInvoices"] = Relationship(back_populates='dr_entries')
    purchase_invoice:Optional["PurchaseInvoices"] = Relationship(back_populates='dr_entries')
    purchase_return_voucher:Optional["PurchaseReturnVouchers"] = Relationship(back_populates='dr_entries')
    sales_return_voucher:Optional["SalesReturnVouchers"] = Relationship(back_populates='dr_entries')
    cr_entries:Optional[List["CrEntries"]] = Relationship(back_populates='dr_entries', link_model=EntryLink)

class CrEntries(EntriesBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    account:"Accounts" = Relationship(back_populates='cr_entries')
    journal_id:Optional[int] = Field(foreign_key='journals.id')
    sales_invoice_id:Optional[int] = Field(foreign_key='salesinvoices.id')
    purchase_invoice_id:Optional[int] = Field(foreign_key='purchaseinvoices.id')
    purchase_return_voucher_id:Optional[int] = Field(foreign_key='purchasereturnvouchers.id')
    sales_return_voucher_id:Optional[int] = Field(foreign_key='salesreturnvouchers.id')
    journal:"Journals" = Relationship(back_populates='cr_entries')
    sales_invoice:Optional["SalesInvoices"] = Relationship(back_populates='cr_entries')
    purchase_invoice:Optional["PurchaseInvoices"] = Relationship(back_populates='cr_entries')
    purchase_return_voucher:Optional["PurchaseReturnVouchers"] = Relationship(back_populates='cr_entries')
    sales_return_voucher:Optional["SalesReturnVouchers"] = Relationship(back_populates='cr_entries')
    dr_entries:Optional[List["DrEntries"]] = Relationship(back_populates='cr_entries', link_model=EntryLink)

