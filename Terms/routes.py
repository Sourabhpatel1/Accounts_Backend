from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from database import get_session
from .models import PurchaseOrderTerms, PurchaseInvoiceTerms, SalesOrderTerms, SalesInvoiceTerms, TermsRequest

term_router = APIRouter(prefix="/terms", tags=['Terms'])

@term_router.post("/po")
def add_po_terms(terms:TermsRequest, session:Session=Depends(get_session)):
    try:
        new_term = PurchaseOrderTerms.from_orm(terms)
        session.add(new_term)
        session.commit()
        session.refresh(new_term)
        return new_term
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )

@term_router.post("/pi")
def add_pi_terms(terms:TermsRequest, session:Session=Depends(get_session)):
    try:
        new_term = PurchaseInvoiceTerms.from_orm(terms)
        session.add(new_term)
        session.commit()
        session.refresh(new_term)
        return new_term
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )

@term_router.post("/so")
def add_pi_terms(terms:TermsRequest, session:Session=Depends(get_session)):
    try:
        new_term = SalesOrderTerms.from_orm(terms)
        session.add(new_term)
        session.commit()
        session.refresh(new_term)
        return new_term
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )

@term_router.post("/si")
def add_pi_terms(terms:TermsRequest, session:Session=Depends(get_session)):
    try:
        new_term = SalesInvoiceTerms.from_orm(terms)
        session.add(new_term)
        session.commit()
        session.refresh(new_term)
        return new_term
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )

@term_router.get("/po")
def read_po_terms(session:Session=Depends(get_session)):
    terms = session.exec(select(PurchaseOrderTerms)).all()
    return terms

@term_router.get("/pi")
def read_po_terms(session:Session=Depends(get_session)):
    terms = session.exec(select(PurchaseInvoiceTerms)).all()
    return terms

@term_router.get("/so")
def read_po_terms(session:Session=Depends(get_session)):
    terms = session.exec(select(SalesOrderTerms)).all()
    return terms

@term_router.get("/si")
def read_po_terms(session:Session=Depends(get_session)):
    terms = session.exec(select(SalesInvoiceTerms)).all()
    return terms
