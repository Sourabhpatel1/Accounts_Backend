from sqlmodel import SQLModel, Session
from database import company_engine

from Business.models import Business

def create_default_company():
    with Session(company_engine) as session:
        default_business = Business(
            name="Default",
            gst="N/A",
            phone=0000000000,
            email="default@default.com",
            street_address="Default",
            city="Default",
            state="Default",
            country="Default",
            postal_code="Default",
            is_active=True
        )