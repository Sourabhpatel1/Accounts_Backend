from sqlmodel import Session, select
from Accounts.models import Accounts, AccountsBase
from Accounts.crud import create_account
from .models import CustomersBase, Customers

def create_customer(customer:CustomersBase, session:Session):
    existing_account = session.exec(select(Accounts).where(Accounts.name == customer.name)).first()
    if existing_account:
        raise ValueError(f"Error : Could not create customer account because an Account with name {customer.name} already exits.")
    new_customer_account_base = AccountsBase(
        name=customer.name,
        group_account_id=32
    )
    new_customer_account = create_account(account=new_customer_account_base, session=session)
    session.add(new_customer_account)
    new_customer = Customers.from_orm(customer, update={
        'account_id' : new_customer_account.id,
        'account' : new_customer_account
    })
    return new_customer