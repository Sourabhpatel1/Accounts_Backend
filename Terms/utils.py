from sqlmodel import Session, select
from database import get_engine
from .models import TermsBase, SalesOrderTerms, SalesInvoiceTerms, PurchaseOrderTerms, PurchaseInvoiceTerms

def create_test_terms():
    with Session(get_engine()) as session:
        terms_base = TermsBase(terms="""Test Terms and Conditions ... 
        Test Terms and Consitions Line 1
        Test Terms and Conditions Line 2
        Test Terms and Conditions Line 3""")
        existing_so_term = session.get(SalesOrderTerms, 1)
        existing_po_term = session.get(PurchaseOrderTerms, 1)
        existing_si_term = session.get(SalesInvoiceTerms, 1)
        existing_pi_term = session.get(PurchaseInvoiceTerms, 1)

        if not (existing_so_term and existing_po_term and existing_si_term and existing_pi_term):
            new_so_term = SalesOrderTerms.from_orm(terms_base)
            new_si_term = SalesInvoiceTerms.from_orm(terms_base)
            new_po_term = PurchaseOrderTerms.from_orm(terms_base)
            new_pi_term = PurchaseInvoiceTerms.from_orm(terms_base)

            session.add(new_so_term)
            session.add(new_si_term)
            session.add(new_po_term)
            session.add(new_pi_term)

            session.commit()
        print("Finished Initializing Test Terms And Conditins")
