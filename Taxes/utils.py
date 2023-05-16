from sqlmodel import Session
from database import get_engine
from .models import TaxesBase, GstInput, GstOutput, IgstInput, IgstOutput
from .crud import create_gst

def create_test_tax():
    with Session(get_engine()) as session:
        e_igst_i = session.get(IgstInput, 1)
        e_igst_o = session.get(IgstOutput, 1)
        e_gst_i = session.get(GstInput, 1)
        e_gst_o = session.get(GstOutput, 1)

        if not (e_igst_o or e_gst_i or e_gst_i or e_gst_o):
           created =  create_gst(tax=TaxesBase(rate=5), session=session)
           if created:
               session.commit()
           else:
               raise ValueError("Failed to create test gst accounts")
    print("Finished Initaializing Taxes")
