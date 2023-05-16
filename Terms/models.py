from datetime import date
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from PurchaseDocs.models import PurchaseOrders, PurchaseInvoices
    from SalesDocs.models import SalesOrders, SalesInvoices

class TermsRequest(SQLModel):
    terms:str

class TermsBase(TermsRequest):
    date_created:date = date.today()

class PurchaseOrderTerms(TermsBase, table=True):
    id:Optional[int] = Field(primary_key=True)
    p_orders:Optional[List["PurchaseOrders"]] = Relationship(back_populates='terms')

class PurchaseInvoiceTerms(TermsBase, table=True):
    id:Optional[int] = Field(primary_key=True)
    p_invoices:Optional[List["PurchaseInvoices"]] = Relationship(back_populates='terms')

class SalesOrderTerms(TermsBase, table=True):
    id:Optional[int] = Field(primary_key=True)
    s_orders:Optional[List["SalesOrders"]] = Relationship(back_populates='terms')

class SalesInvoiceTerms(TermsBase, table=True):
    id:Optional[int] = Field(primary_key=True)
    s_invoices:Optional[List["SalesInvoices"]] = Relationship(back_populates='terms')
