from sqlmodel import Session, select
from Accounts.models import Accounts, AccountsBase
from Accounts.crud import create_account
from .models import VendorsBase, Vendors

def create_vendor(vendor:VendorsBase, session:Session):
    existing_account = session.exec(select(Accounts).where(Accounts.name == vendor.name)).first()
    if existing_account:
        raise ValueError(f"Error : Could not create vendor account because an Account with name {vendor.name} already exits.")
    new_vendor_account_base = AccountsBase(
        name=vendor.name,
        sub_group_id=210
    )
    new_vendor_account = create_account(account=new_vendor_account_base, session=session)
    session.add(new_vendor_account)
    new_customer = Vendors.from_orm(vendor, update={
        'account_id' : new_vendor_account.id,
        'account' : new_vendor_account
    })
    return new_customer