from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import SQLModel, Session, select
from pydantic import ValidationError
from database import create_main_db_and_tables, get_company_session, get_engine
from .models import BusinessBase, Business

from Accounts.models import PrimaryAccounts, Accounts, GroupAccounts, SubGroups
from Customers.models import Customers
from Departments.models import Departments
from Employees.models import Employees
from Entries.models import DrEntries, CrEntries
from Inventory.models import InventoryItems, POLineItems, PILineItems, SOLineItems, SILineItems, Stocks
from Journals.models import Journals
from PurchaseDocs.models import PurchaseOrders, PurchaseInvoices
from SalesDocs.models import SalesOrders, SalesInvoices
from Vendors.models import Vendors
from Terms.models import PurchaseOrderTerms, PurchaseInvoiceTerms, SalesOrderTerms, SalesInvoiceTerms
from Taxes.models import GstInput, GstOutput, IgstOutput, IgstInput

from Accounts.utils import initialize_primary_accounts, initialize_group_accounts, initialize_accounts, initialize_sub_groups
from Customers.utils import create_test_customer
from Inventory.utils import create_test_units, create_test_item
from Taxes.utils import create_test_tax
from Terms.utils import create_test_terms
from Vendors.utils import create_test_vendor
        

business_router = APIRouter(prefix='/business', tags=["Business"])

@business_router.post("/")
def add_new_business(business:BusinessBase, session:Session=Depends(get_company_session)):
    try:
        active_business = session.exec(select(Business).where(Business.is_active)).first()
        
        if active_business:
            active_business.is_active = False
            session.add(active_business)

        new_business = Business.from_orm(business, update={"is_active" : True})
        
        session.add(new_business)
        session.commit()
        session.refresh(new_business)
        
        SQLModel.metadata.create_all(get_engine())

        create_main_db_and_tables()
        
        initialize_primary_accounts()
        initialize_group_accounts()
        initialize_sub_groups()
        initialize_accounts()
        create_test_units()
        create_test_customer()
        create_test_terms()
        create_test_tax()
        create_test_vendor()
        create_test_item()

      
        return new_business
    
    except Exception as e:
        print(e)
        message = str(e)
        if isinstance(e, ValidationError):
            message = " ".join(str(e).split("\n")[2].strip().split(" ")[:-1])
        raise HTTPException(status_code=422, detail=message)

@business_router.get("/")
def read_active_business(session:Session=Depends(get_company_session)):
    active_business = session.exec(select(Business).where(Business.is_active)).first()
    return active_business

@business_router.get("/all")
def read_all_business(session:Session=Depends(get_company_session)):
    business = session.exec(select(Business)).all()
    return business

@business_router.patch("/{id}")
def set_active_business(id:int, session:Session=Depends(get_company_session)):
    business = session.get(Business, id)
    active_business = session.exec(select(Business).where(Business.is_active)).first()

    if business == active_business:
        return business

    if not business:
        raise HTTPException(status_code=404, detail=f"Business with id {id} does not exist.")
    
    business.is_active = True
    active_business.is_active = False

    session.add(business)
    session.add(active_business)

    session.commit()

    session.refresh(business)

    return business
