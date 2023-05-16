from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from base import base_router
from database import get_session, create_main_db_and_tables
from Accounts.utils import initialize_primary_accounts, initialize_group_accounts, initialize_accounts
from Customers.utils import create_test_customer
from Inventory.utils import create_test_units, create_test_item
from Taxes.utils import create_test_tax
from Terms.utils import create_test_terms
from Vendors.utils import create_test_vendor

app = FastAPI()

origins = [
    "https://svelte-kit-production-2c2e.up.railway.app/",
    "https://localhost:5173",
    "https://localhost:4173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_methods=["*"]
)


app.include_router(base_router)

@app.get("/")
def home(session:Session=Depends(get_session)):
    try:
        return "Hello From Accounting App"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))