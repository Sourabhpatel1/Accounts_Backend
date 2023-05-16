from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship
from field_types import DocumentTypes, StateType, OrderStatus, TransactionTypes
if TYPE_CHECKING:
    from Entries.models import DrEntries, CrEntries
    from Inventory.models import SOLineItems, SILineItems, SRLineItems
    from Customers.models import Customers
    from Terms.models import SalesOrderTerms, SalesInvoiceTerms

class SaleBase(SQLModel):
    doc_date:date
    doc_number:int
    customer_id:int = Field(foreign_key='customers.id')
    state_type:StateType

class SalesOrderBase(SaleBase):
    terms_id:Optional[int] = Field(foreign_key='salesorderterms.id')

class SalesOrders(SalesOrderBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    doc_prefix:str = "S.O.-"
    doc_type:DocumentTypes = DocumentTypes.SalesOrder
    timestamp:datetime = datetime.utcnow()
    line_items:Optional[List["SOLineItems"]] = Relationship(back_populates='so')
    customer:"Customers" = Relationship(back_populates='s_orders')
    status:OrderStatus = OrderStatus.Pending
    terms:Optional["SalesOrderTerms"] = Relationship(back_populates='s_orders')
    invoices:Optional[List["SalesInvoices"]] = Relationship(back_populates='sales_order')

class SalesInvoiceBase(SaleBase):
    transaction_type:TransactionTypes
    so_id:Optional[int] = Field(foreign_key='salesorders.id')
    terms_id:Optional[int] = Field(foreign_key='salesinvoiceterms.id')
    rounded_off:Optional[float] = None

class SalesInvoices(SalesInvoiceBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    doc_prefix:str = "S.Inv.-"
    doc_type:DocumentTypes = DocumentTypes.SalesInvoice
    timestamp:datetime = datetime.utcnow()
    sales_order:Optional["SalesOrders"] = Relationship(back_populates='invoices')
    dr_entries:Optional[List["DrEntries"]] = Relationship(back_populates='sales_invoice')
    cr_entries:Optional[List["CrEntries"]] = Relationship(back_populates='sales_invoice')
    line_items:Optional[List["SILineItems"]] = Relationship(back_populates='si')
    customer:"Customers" = Relationship(back_populates='s_invoices')
    terms:Optional["SalesInvoiceTerms"] = Relationship(back_populates='s_invoices')
    return_vouchers:Optional[List["SalesReturnVouchers"]] = Relationship(back_populates='sales_invoice')

class SalesReturnVoucherBase(SaleBase):
    si_id:int = Field(foreign_key='salesinvoices.id')
    

class SalesReturnVouchers(SalesReturnVoucherBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    doc_prefix:str = "S.Ret.-"
    doc_type:DocumentTypes = DocumentTypes.SalesReturnVoucher
    timestamp:datetime = datetime.utcnow()
    customer:"Customers" = Relationship(back_populates='return_vouchers')
    sales_invoice:"SalesInvoices" = Relationship(back_populates='return_vouchers')
    line_items:Optional[List["SRLineItems"]] = Relationship(back_populates='sr')
    dr_entries:Optional[List["DrEntries"]] = Relationship(back_populates='sales_return_voucher')
    cr_entries:Optional[List["CrEntries"]] = Relationship(back_populates='sales_return_voucher')

class ReceiptRequest(SQLModel):
    receipt_account_id:int
    customer_id:int 
    si_id:int 
    amount:float