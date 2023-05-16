from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, Session, select
from database import get_session
from .models import InventoryItems, InventoryItemsBase, Units, Stocks, UnitsRequest
from .crud import create_inventory_item

inventory_router = APIRouter(prefix="/inventory", tags=["Inventory"])

@inventory_router.get("/")
def read_all_inventory_items(session:Session=Depends(get_session)):
    inventory = session.exec(select(InventoryItems)).all()
    return [
        {   
            "id" : i.id,
            "name" : i.name,
            "unit" : i.unit.name,
            "unit_id" : i.unit_id,
            'gst_rate' : i.igst_input.rate,
            "available_stock" : sum([s.quantity for s in i.stocks])
        } for i in inventory
    ]

@inventory_router.get("/{id}")
def read_inventory_by_id(id:int, session:Session=Depends(get_session)):
    inventory = session.get(InventoryItems, id)
    if not inventory:
        raise HTTPException(
            status_code=404, detail=f"Inventory with id {id} does not exist."
        )
    return {   
            "id" : inventory.id,
            "name" : inventory.name,
            "unit" : inventory.unit.name,
            "unit_id" : inventory.unit_id,
            'gst_rate' : inventory.igst_input.rate,
            "available_stock" : sum([s.quantity for s in inventory.stocks])
    }

@inventory_router.get("/units/")
def read_all_units(session:Session=Depends(get_session)):
    units = session.exec(select(Units)).all()
    return units

@inventory_router.post("/")
def add_inventory_item(item:InventoryItemsBase, session:Session=Depends(get_session)):
    try:
        new_inventory_item = create_inventory_item(inventory=item)
        session.add(new_inventory_item)
        session.commit()
        session.refresh(new_inventory_item)
        return new_inventory_item
    except Exception as e:
        raise HTTPException(
            status_code=403, detail=str(e)
        )

@inventory_router.get("/stocks/")
def read_inventory_stocks(session:Session=Depends(get_session)):
    stocks = session.exec(select(Stocks)).all()
    return [
        {
            "id" : stock.id,
            "item_id" : stock.item.id,
            "name" : stock.item.name,
            "unit" : stock.item.unit.name,
            "purchase_date" : stock.line_item.pi.doc_date,
            "quantity" : stock.line_item.quantity,
            "price" : stock.line_item.price,
            "purchase_invoice" : stock.line_item.pi.doc_number,
            "available_stock" : stock.quantity,
        } for stock in stocks
    ]

@inventory_router.post("/units")
def add_new_unit(unit:UnitsRequest, session:Session=Depends(get_session)):
    try:
        new_unit = Units.from_orm(unit)
        session.add(new_unit)
        session.commit()
        session.refresh(new_unit)
        return new_unit
    except Exception as e:
        raise HTTPException(
            status_code=403, detail=str(e)
        )