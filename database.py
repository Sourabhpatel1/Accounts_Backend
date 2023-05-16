from sqlmodel import SQLModel, Session, select, create_engine
from Business.models import Business


connect_args = {"check_same_thread" : False}
company_file_name = "Business.db"
company_database_url = f"sqlite:///{company_file_name}"
company_engine = create_engine(company_database_url, connect_args=connect_args)

def get_active_business():
    with Session(company_engine) as session:
        active_business = session.exec(select(Business).where(Business.is_active)).first()
        if not active_business:
            return None
        return active_business.name

def get_company_session():
    with Session(company_engine) as session:
        yield session

SQLModel.metadata.create_all(company_engine)

def create_main_db_and_tables():
    file_name = get_active_business() + ".db"
    db_url = f"sqlite:///{file_name}"
    eg = create_engine(db_url, connect_args=connect_args)
    SQLModel.metadata.create_all(eg)
    Business.__table__.drop(eg)

def get_session():
    file_name = get_active_business() + ".db"
    db_url = f"sqlite:///{file_name}"
    eg = create_engine(db_url, connect_args=connect_args)
    with Session(eg) as session:
        yield session

def get_engine():
    file_name = get_active_business() + ".db"
    db_url = f"sqlite:///{file_name}"
    eg = create_engine(db_url, connect_args=connect_args)
    return eg