from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship
from field_types import DocumentTypes, StateType, OrderStatus, TransactionTypes
if TYPE_CHECKING:
    from Entries.models import DrEntries, CrEntries
    from Inventory.models import POLineItems, PILineItems, PRLineItems
    from Vendors.models import Vendors
    from Terms.models import PurchaseOrderTerms, PurchaseInvoiceTerms

class PurchaseBase(SQLModel):
    doc_date:date
    doc_number:int
    vendor_id:int = Field(foreign_key='vendors.id')
    state_type:StateType

class PurchaseOrderBase(PurchaseBase):
    terms_id:Optional[int] = Field(foreign_key='purchaseorderterms.id')

class PurchaseOrders(PurchaseOrderBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    doc_prefix:str = "P.O.-"
    doc_type:DocumentTypes = DocumentTypes.PurchaseOrder
    timestamp:datetime = datetime.utcnow()
    line_items:Optional[List["POLineItems"]] = Relationship(back_populates='po')
    vendor:"Vendors" = Relationship(back_populates='p_orders')
    purchase_invoices:Optional[List["PurchaseInvoices"]] = Relationship(back_populates='purchase_order')
    status:OrderStatus = OrderStatus.Pending
    terms:Optional["PurchaseOrderTerms"] = Relationship(back_populates='p_orders')

class PurchaseInvoicesBase(PurchaseBase):
    po_id:Optional[int] = Field(foreign_key='purchaseorders.id')
    transaction_type:TransactionTypes
    terms_id:Optional[int] = Field(foreign_key='purchaseinvoiceterms.id')
    rounded_off:Optional[float] = 0.00

class PurchaseInvoices(PurchaseInvoicesBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    doc_prefix:str = "P.Inv.-"
    doc_type:DocumentTypes = DocumentTypes.PurchaseInvoice
    timestamp:datetime = datetime.utcnow()
    purchase_order:Optional["PurchaseOrders"] = Relationship(back_populates='purchase_invoices')
    dr_entries:Optional[List["DrEntries"]] = Relationship(back_populates='purchase_invoice')
    cr_entries:Optional[List["CrEntries"]] = Relationship(back_populates='purchase_invoice')
    line_items:Optional[List["PILineItems"]] = Relationship(back_populates='pi')
    vendor:"Vendors" = Relationship(back_populates='p_invoices')
    terms:Optional["PurchaseInvoiceTerms"] = Relationship(back_populates='p_invoices')
    return_vouchers:Optional[List["PurchaseReturnVouchers"]] = Relationship(back_populates='purchase_invoice')

class PurchaseReturnVoucherBase(PurchaseBase):
    pi_id:int = Field(foreign_key='purchaseinvoices.id')
    
class PurchaseReturnVouchers(PurchaseReturnVoucherBase, table=True):
    id:Optional[int] = Field(primary_key=True, index=True)
    doc_prefix:str = "P.Ret.-"
    doc_type:DocumentTypes = DocumentTypes.PurchaseReturnVoucher
    timestamp:datetime = datetime.utcnow()
    vendor:"Vendors" = Relationship(back_populates='return_vouchers')
    purchase_invoice:"PurchaseInvoices" = Relationship(back_populates='return_vouchers')
    line_items:Optional[List["PRLineItems"]] = Relationship(back_populates='pr')
    dr_entries:Optional[List["DrEntries"]] = Relationship(back_populates='purchase_return_voucher')
    cr_entries:Optional[List["CrEntries"]] = Relationship(back_populates='purchase_return_voucher')
    
class PayementRequest(SQLModel):
    payment_account_id:int
    vendor_id:int
    pi_id:int 
    amount:float
