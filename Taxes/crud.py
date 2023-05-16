from sqlmodel import Session, select
from Accounts.models import AccountsBase
from Accounts.crud import create_account
from .models import GstOutput, GstInput, IgstInput, IgstOutput, TaxesBase

def create_gst(tax:TaxesBase, session:Session) -> bool:
    gst_account_input = session.exec(select(GstInput).where(GstInput.rate == tax.rate)).first()
    gst_account_output = session.exec(select(GstOutput).where(GstOutput.rate == tax.rate)).first()
    igst_account_input = session.exec(select(IgstInput).where(IgstInput.rate == tax.rate)).first()
    igst_account_output = session.exec(select(IgstOutput).where(IgstOutput.rate == tax.rate)).first()

    if igst_account_input or igst_account_output or gst_account_input or gst_account_output:
        raise ValueError(f"GST accounts with a tax rate of {tax.rate} alrady exists.")
    
    gst_ouput_account_base = AccountsBase(name=f"GST (Output)-{tax.rate}%", sub_group_id=211)
    gst_input_account_base = AccountsBase(name=f"GST (Input)-{tax.rate}%", sub_group_id=324)
    igst_output_account_base = AccountsBase(name=f"IGST (Output)-{tax.rate}%", sub_group_id=212)
    igst_input_account_base = AccountsBase(name=f"IGST (Input)-{tax.rate}%", sub_group_id=325)

    new_output_gst_account = create_account(account=gst_ouput_account_base, session=session)
    new_input_gst_account = create_account(account=gst_input_account_base, session=session)
    new_output_igst_account = create_account(account=igst_output_account_base, session=session)
    new_input_igst_account = create_account(account=igst_input_account_base, session=session)

    session.add(new_output_gst_account)
    session.add(new_input_gst_account)
    session.add(new_output_igst_account)
    session.add(new_input_igst_account)

    new_gst_output = GstOutput(
        name=f"GST (Output)-{tax.rate}%",
        rate=tax.rate,
        account_id=new_output_gst_account.id,
        account=new_output_gst_account
    )

    new_gst_input = GstInput(
        name=f"GST (Input)-{tax.rate}%",
        rate=tax.rate,
        account_id=new_input_gst_account.id,
        account=new_input_gst_account
    )

    new_igst_output = IgstOutput(
        name=f"IGST (Output)-{tax.rate}%",
        rate=tax.rate,
        account_id=new_output_igst_account.id,
        account=new_output_igst_account
    )

    new_igst_input = IgstInput(
        name=f"IGST (Input)-{tax.rate}%",
        rate=tax.rate,
        account_id=new_input_igst_account.id,
        account=new_input_igst_account
    )

    session.add(new_gst_output)
    session.add(new_gst_input)
    session.add(new_igst_output)
    session.add(new_igst_input)

    return True

    





































# def create_gst_output(gst:TaxesBase, session:Session):
#     existing_account = session.exec(select(Accounts).where(Accounts.name == gst.name)).first()
#     if existing_account:
#         raise ValueError(f"GST Input account with name {gst.name} already exists")
#     new_account_base = AccountsBase(
#         name=gst.name, sub_group_id=23
#     )
#     new_gst_account = create_account(account=new_account_base, session=session)
#     session.add(new_gst_account)
#     new_tax = Taxes.from_orm(gst, update={
#         'account_id' : new_gst_account.id,
#         'account' : new_gst_account
#     })
#     return new_tax

# def create_igst_output(gst:TaxesBase, session:Session):
#     existing_account = session.exec(select(Accounts).where(Accounts.name == gst.name)).first()
#     if existing_account:
#         raise ValueError(f"IGST Input account with name {gst.name} already exists")
#     new_account_base = AccountsBase(
#         name=gst.name, sub_group_id=24
#     )
#     new_gst_account = create_account(account=new_account_base, session=session)
#     session.add(new_gst_account)
#     new_tax = Taxes.from_orm(gst, update={
#         'account_id' : new_gst_account.id,
#         'account' : new_gst_account
#     })
#     return new_tax
