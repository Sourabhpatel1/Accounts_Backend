from sqlmodel import Session, select
from database import get_engine
from .models import Units, InventoryItemsBase, InventoryItems, ItemTypes, ItemCategory
from .crud import create_inventory_item

units = ["Numbers", "Kilogram", "Grams", "Miligrams", "Kiloliters", "Liters", "Mililiters", "Quintals", "M.T.", "Meters", "Centimeters", "Milimeters", "Feet", "Inch", "Sq.Meters", "Sq.Feet", "Sq.Inch"]

def create_test_item()->None:
    with Session(get_engine()) as session:
        existing_item = session.get(InventoryItems, 1)
        if not existing_item:
            test_inventory_item_base = InventoryItemsBase(
                name="Test Item 1",
                unit_id=1,
                inventory_account_id=3222,
                item_type=ItemTypes.Trade,
                item_category=ItemCategory.Finished,
                gst_input_id=1,
                igst_input_id=1,
                gst_output_id=1,
                igst_output_id=1
            )
            test_inventory_item = create_inventory_item(inventory=test_inventory_item_base)
            test_inventory_item_base.name = "Test Item 2"
            test_inventory_item_2 = create_inventory_item(inventory=test_inventory_item_base)
            session.add(test_inventory_item)
            session.add(test_inventory_item_2)
            session.commit()
    print("Finished initializing Test Inventory")


def create_test_units() -> None:
    with Session(get_engine()) as session:
        for unit in units:
            old_unit = session.exec(select(Units).where(Units.name == unit)).first()
            if not old_unit:
                new_unit = Units(name=unit)
                session.add(new_unit)
                session.commit()
    print("Finished Creating Units")
    