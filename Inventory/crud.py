from sqlmodel import Session, select
from .models import (
    InventoryItemsBase,
    InventoryItems,
)

def create_inventory_item(inventory:InventoryItemsBase):
    new_inventory_item = InventoryItems.from_orm(inventory)
    return new_inventory_item
