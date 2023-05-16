from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from .models import CustomersBase, Customers
from .crud import create_customer

customer_router = APIRouter(prefix="/customer", tags=["Customers"])

@customer_router.get("/")
def read_all_customers(session:Session=Depends(get_session)):
    customers = session.exec(select(Customers)).all()
    return customers

@customer_router.get("/{id}")
def read_customer_by_id(id:int, session:Session=Depends(get_session)):
    customer = session.get(Customers, id)
    if not customer:
        raise HTTPException(
            status_code=404, detail=f"Customer with id {id} does not exist."
        )
    return customer

@customer_router.post("/")
def add_new_customer(customer:CustomersBase, session:Session=Depends(get_session)):
    try:
        new_customer = create_customer(customer=customer, session=session)
        session.add(new_customer)
        session.commit()
        session.refresh(new_customer)
        return new_customer
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))