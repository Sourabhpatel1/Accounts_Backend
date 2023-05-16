from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from .models import TaxesBase, GstInput, GstOutput, IgstInput, IgstOutput
from .crud import create_gst

tax_router = APIRouter(prefix="/tax", tags=["Taxes"])

@tax_router.get("/")
def read_all_taxes(session:Session=Depends(get_session)):
    gst_input = session.exec(select(GstInput)).all()
    gst_output = session.exec(select(GstOutput)).all()
    igst_input = session.exec(select(IgstInput)).all()
    igst_output = session.exec(select(IgstOutput)).all()

    return {
        "gst_input" : gst_input,
        "gst_output" : gst_output,
        "igst_input" : igst_input,
        "igst_output" : igst_output,
    }

@tax_router.post("/")
def create_tax(tax:TaxesBase, session:Session=Depends(get_session)):
    try:
        status = create_gst(tax=tax, session=session)
        if status:
            session.commit()
            return {
                'message' : f'Taxes with tax rate {tax.rate} created succesfully.'
            }
    except Exception as e:
        raise HTTPException(
            status_code=403, detail = str(e)
        )
