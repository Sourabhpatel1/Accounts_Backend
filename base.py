from fastapi import APIRouter
from Business.routes import business_router
from Accounts.routes import acc_router
from Customers.routes import customer_router
from Dashboard.routes import dash_router
from Departments.routes import dep_router
from Employees.routes import emp_router
from Inventory.routes import inventory_router
from Journals.routes import journal_router
from PurchaseDocs.routes import purchase_router
from Reports.routes import reports_router
from SalesDocs.routes import sale_router
from Taxes.routes import tax_router
from Terms.routes import term_router
from Vendors.routes import vendor_router

base_router = APIRouter(prefix="")

base_router.include_router(business_router)
base_router.include_router(acc_router)
base_router.include_router(customer_router)
base_router.include_router(dash_router)
base_router.include_router(dep_router)
base_router.include_router(emp_router)
base_router.include_router(inventory_router)
base_router.include_router(journal_router)
base_router.include_router(purchase_router)
base_router.include_router(reports_router)
base_router.include_router(sale_router)
base_router.include_router(tax_router)
base_router.include_router(term_router)
base_router.include_router(vendor_router)