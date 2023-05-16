from typing import Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from .utils import (
    get_current_ratio, 
    get_cash_ratio, 
    get_profit_ratios, 
    get_debt_ratios, 
    get_sales_quantities,
    get_purchase_quantities,
    get_party_data,
    get_cash_data
)


current_start = date(date.today().year, 4, 1)
current_end = date(date.today().year + 1, 3, 31)

dash_router = APIRouter(prefix="/dash", tags=["DashBoard"])

@dash_router.get("/liquidity")
def read_liquidity_ratios(start:Optional[str]=None, end:Optional[str] = None, session:Session = Depends(get_session)):
    
    if start is not None:
        start = datetime.strptime(start, '%d-%m-%Y').date()
    
    if end is not None:
        end = datetime.strptime(end, '%d-%m-%Y').date()

    if not start:
        start = current_start
    
    if not end:
        end = current_end

    current_ratio = get_current_ratio(start=start, end=end, session=session)
    cash_ratio = get_cash_ratio(start=start, end=end, session=session)

    return {
        "Current Ratio" : current_ratio,
        "Cash Ratio" : cash_ratio
    }

@dash_router.get("/profitability")
def read_profitability_ratios(start:Optional[str] = None, end:Optional[str]=None, session:Session=Depends(get_session)):
    if start is not None:
        start = datetime.strptime(start, '%d-%m-%Y').date()

    if end is not None:
        end = datetime.strptime(end, '%d-%m-%Y').date()

    if not start:
        start = current_start
    
    if not end:
        end = current_end

    ratios = get_profit_ratios(start=start, end=end, session=session)

    return ratios

@dash_router.get("/debt")
def read_debt_ratios(start:Optional[str]=None, end:Optional[str]=None, session:Session=Depends(get_session)):
    if start is not None:
        start = datetime.strptime(start, '%d-%m-%Y').date()

    if end is not None:
        end = datetime.strptime(end, '%d-%m-%Y').date()

    if not start:
        start = current_start
    
    if not end:
        end = current_end

    ratios = get_debt_ratios(start=start, end=end, session=session)

    return ratios

@dash_router.get("/item_quantity")
def get_quantities(session:Session=Depends(get_session)):
    # sales_invoices = session.exec(select)
    s = get_sales_quantities(session=session)
    p = get_purchase_quantities(session=session)
    return {
        "sold" : sorted([{k : v} for k, v in s.items()], key=lambda x : list(x.keys())[0])[:6],
        "pur" : sorted([{k : v} for k, v in p.items()], key=lambda x : list(x.keys())[0])[:6],
    }

@dash_router.get("/party_data")
def get_data_of_parties(session:Session=Depends(get_session)):
    c, v = get_party_data(session=session)
    return {
        "customer_data" : sorted(c, key=lambda x : x[list(x.keys())[0]])[:6],
        "vendor_data" : sorted(v, key=lambda x : x[list(x.keys())[0]])[:6],
    }

@dash_router.get("/cash_data")
def get_cash_and_bank(session:Session=Depends(get_session)):
    cash_dr, cash_cr, bank_dr, bank_cr = get_cash_data(session=session)
    return {
        'c_dr' : cash_dr,
        'c_cr' : cash_cr,
        'b_dr' : bank_dr,
        'b_cr' : bank_cr
    }