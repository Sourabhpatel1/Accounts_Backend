from sqlmodel import Session, select
from database import get_engine
from Accounts.models import AccountsBase
from Accounts.crud import create_account
from .models import Vendors, VendorsBase

def create_test_vendor() -> None:
    with Session(get_engine()) as session:
        existing_vendor = session.exec(select(Vendors)).all()
        
        if not existing_vendor:
            new_vendor_account_base = AccountsBase(
                name="Test vendor",
                sub_group_id=210
            )
            new_vendor_account = create_account(account=new_vendor_account_base, session=session)
            
            session.add(new_vendor_account)
            
            new_vendor_base = VendorsBase(
                name="Test Vendor",
                gst="N/A",
                phone=9876543210,
                email="vendor@test.com",
                street_address="Test Vendor's Street Address, ABC Lane.",
                city="Test City",
                state="Test State",
                country="Test Country",
                postal_code=123456
            )

            new_vendor = Vendors.from_orm(new_vendor_base, update={
                'account_id' : new_vendor_account.id,
                'account' : new_vendor_account
            })

            session.add(new_vendor)
            session.commit()
    print("Finished Initializing Test Vendor")