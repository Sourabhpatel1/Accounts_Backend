from typing import Optional, List, TYPE_CHECKING
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from Accounts.models import Accounts
    from PurchaseDocs.models import PurchaseOrders, PurchaseInvoices, PurchaseReturnVouchers
    from SalesDocs.models import SalesOrders, SalesInvoices, SalesReturnVouchers
    from Taxes.models import GstOutput, GstInput, IgstInput, IgstOutput


class ItemTypes(Enum):
    Trade: str = "Trade"
    Store: str = "Store"

class ItemCategory(Enum):
    Raw:int = 0
    Unfinished:int = 1
    Finished:int = 2

class stock_si_item_link(SQLModel, table=True):
    stock_id: Optional[int] = Field(
        default=None, foreign_key='stocks.id', primary_key=True
    )
    sale_line_item_id: Optional[int] = Field(
        default=None, foreign_key='silineitems.id', primary_key=True
    )


class StockSaleReturnLineItemLink(SQLModel, table=True):
    stock_id: Optional[int] = Field(
        default=None, foreign_key='stocks.id', primary_key=True
    )
    sr_line_item_id: Optional[int] = Field(
        default=None, foreign_key='srlineitems.id', primary_key=True
    )


class InventoryItemsBase(SQLModel):
    name: str = Field(index=True, unique=True)
    unit_id: int = Field(foreign_key='units.id')
    gst_input_id: int = Field(foreign_key='gstinput.id')
    gst_output_id: int = Field(foreign_key='gstoutput.id')
    igst_input_id: int = Field(foreign_key='igstinput.id')
    igst_output_id: int = Field(foreign_key='igstoutput.id')
    inventory_account_id: int = Field(foreign_key='accounts.id')
    item_type: ItemTypes
    item_category:ItemCategory


class InventoryItems(InventoryItemsBase, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    inventory_account: "Accounts" = Relationship(back_populates='inventory_items')
    unit: "Units" = Relationship(back_populates='items')
    stocks: Optional[List["Stocks"]] = Relationship(back_populates='item')
    po_line_items: Optional[List["POLineItems"]] = Relationship(back_populates='item')
    pi_line_items: Optional[List["PILineItems"]] = Relationship(back_populates='item')
    so_line_items: Optional[List["SOLineItems"]] = Relationship(back_populates='item')
    si_line_items: Optional[List["SILineItems"]] = Relationship(back_populates='item')
    pr_line_items: Optional[List["PRLineItems"]] = Relationship(back_populates='item')
    sr_line_items: Optional[List["SRLineItems"]] = Relationship(back_populates='item')
    gst_output: Optional["GstOutput"] = Relationship(back_populates='items')
    igst_output: Optional["IgstOutput"] = Relationship(back_populates='items')
    gst_input: Optional["GstInput"] = Relationship(back_populates='items')
    igst_input: Optional["IgstInput"] = Relationship(back_populates='items')


class LineItemBase(SQLModel):
    item_id: int = Field(foreign_key='inventoryitems.id')
    price: float
    quantity: float
    discount_rate: float
    discount_amount: float


class POLineItems(LineItemBase, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    po_id: int = Field(foreign_key='purchaseorders.id')
    po: "PurchaseOrders" = Relationship(back_populates='line_items')
    item: "InventoryItems" = Relationship(back_populates='po_line_items')


class PILineItems(LineItemBase, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    pi_id: int = Field(foreign_key='purchaseinvoices.id')
    pi: "PurchaseInvoices" = Relationship(back_populates='line_items')
    pr_line_item: Optional["PRLineItems"] = Relationship(back_populates='pi_line_item')
    item: "InventoryItems" = Relationship(back_populates='pi_line_items')
    stock: Optional["Stocks"] = Relationship(sa_relationship_kwargs={'uselist': False}, back_populates='line_item')


class SOLineItems(LineItemBase, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    so_id: int = Field(foreign_key='salesorders.id')
    so: "SalesOrders" = Relationship(back_populates='line_items')
    item: "InventoryItems" = Relationship(back_populates='so_line_items')


class SILineItems(LineItemBase, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    si_id: int = Field(foreign_key='salesinvoices.id')
    si: "SalesInvoices" = Relationship(back_populates='line_items')
    item: "InventoryItems" = Relationship(back_populates='si_line_items')
    sr_line_item: Optional["SRLineItems"] = Relationship(back_populates='si_line_item')
    stocks: Optional[List["Stocks"]] = Relationship(back_populates='sale_line_items', link_model=stock_si_item_link)
    cogs: Optional[float] = 0


class PRLineItemsBase(SQLModel):
    quantity: float
    pi_line_item_id: int = Field(foreign_key='pilineitems.id')


class PRLineItems(PRLineItemsBase, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    item_id: int = Field(foreign_key='inventoryitems.id')
    item: "InventoryItems" = Relationship(back_populates='pr_line_items')
    pi_line_item: "PILineItems" = Relationship(back_populates='pr_line_item')
    pr_id: int = Field(foreign_key='purchasereturnvouchers.id')
    pr: "PurchaseReturnVouchers" = Relationship(back_populates='line_items')
    stock_id: int = Field(foreign_key='stocks.id')
    stock: "Stocks" = Relationship(back_populates='pr_line_item')


class SRLineItemsBase(SQLModel):
    si_line_item_id: int = Field(foreign_key='silineitems.id')
    quantity: float


class SRLineItems(SRLineItemsBase, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    item_id: int = Field(foreign_key='inventoryitems.id')
    item: "InventoryItems" = Relationship(back_populates='sr_line_items')
    si_line_item: "SILineItems" = Relationship(back_populates='sr_line_item')
    sr_id: int = Field(foreign_key='salesreturnvouchers.id')
    sr: "SalesReturnVouchers" = Relationship(back_populates='line_items')
    stock_id: int = Field(foreign_key='stocks.id')
    stocks: Optional[List["Stocks"]] = Relationship(back_populates='sr_line_items', link_model=StockSaleReturnLineItemLink)
    cogs: Optional[float] = 0


class Stocks(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    item_id: int = Field(foreign_key='inventoryitems.id')
    line_item_id: int = Field(foreign_key='pilineitems.id')
    quantity: float
    price: float
    item: "InventoryItems" = Relationship(back_populates='stocks')
    line_item: "PILineItems" = Relationship(back_populates='stock')
    sale_line_items: Optional[List["SILineItems"]] = Relationship(back_populates='stocks', link_model=stock_si_item_link)
    pr_line_item: Optional[List["PRLineItems"]] = Relationship(back_populates='stock')
    sr_line_items: Optional[List["SRLineItems"]] = Relationship(back_populates='stocks', link_model=StockSaleReturnLineItemLink)


class UnitsRequest(SQLModel):
    name:str

class Units(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    name: str
    items: Optional[List["InventoryItems"]] = Relationship(back_populates='unit')
