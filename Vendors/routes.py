from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from .models import Vendors, VendorsBase
from .crud import create_vendor

vendor_router = APIRouter(prefix="/vendor", tags=["Vendors"])

@vendor_router.get("/")
def read_all_vendors(session:Session=Depends(get_session)):
    vendors = session.exec(select(Vendors)).all()
    return vendors

@vendor_router.get("/{id}")
def read_vendor_by_id(id:int, session:Session=Depends(get_session)):
    vendor = session.get(Vendors, id)
    if not vendor:
        raise HTTPException(
            status_code=404, detail=f"Vendor with id {id} does not exist."
        )
    return vendor

@vendor_router.post("/")
def add_new_vendor(vendor:VendorsBase, session:Session=Depends(get_session)):
    try:
        new_vendor = create_vendor(vendor=vendor, session=session)
        session.add(new_vendor)
        session.commit()
        session.refresh(new_vendor)
        return new_vendor
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))