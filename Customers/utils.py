from sqlmodel import Session, select
from database import get_engine
from Accounts.models import AccountsBase
from Accounts.crud import create_account
from .models import Customers, CustomersBase

def create_test_customer() -> None:
    with Session(get_engine()) as session:
        existing_customer = session.exec(select(Customers)).all()
        
        if not existing_customer:
            new_customer_account_base = AccountsBase(
                name="Test Customer",
                sub_group_id=320
            )
            new_customer_account = create_account(account=new_customer_account_base, session=session)
            
            session.add(new_customer_account)
            
            new_customer_base = CustomersBase(
                name="Test Customer",
                gst="N/A",
                phone=9876543210,
                email="customer@test.com",
                street_address="Test Customer's Street Address, ABC Lane.",
                city="Test City",
                state="Test State",
                country="Test Country",
                postal_code=123456
            )

            new_customer = Customers.from_orm(new_customer_base, update={
                'account_id' : new_customer_account.id,
                'account' : new_customer_account
            })

            session.add(new_customer)
            session.commit()
    print("Finished Initializing Test Customer")