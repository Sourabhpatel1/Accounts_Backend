from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from .models import PrimaryAccounts, GroupAccountsBase, GroupAccounts, Accounts, AccountsBase, SubGroups, SubGroupBase
from .crud import create_group_account, create_account
from .utils import get_doc, make_ledger

import pandas as pd

acc_router = APIRouter(prefix="/accounts", tags=["Accounts"])


@acc_router.get("/")
def read_all_primary_accounts_and_children(session: Session=Depends(get_session)):
    primary_accounts = session.exec(select(PrimaryAccounts)).all()
    group_accounts = session.exec(select(GroupAccounts)).all()
    sub = session.exec(select(SubGroups)).all()
    accounts = session.exec(select(Accounts)).all()

    return {
        "primary_accounts": primary_accounts,
        "group_accounts": group_accounts,
        "sub" : sub,
        "accounts": accounts
    }

@acc_router.get("/account_balances/{id}")
def read_account_balances(id:int, session:Session=Depends(get_session)):
    account = session.get(Accounts, id)
    if not account:
        raise HTTPException(status_code=404, detail=f"Account with id {id} does not exists.")
    
    b_type = 1 if account.sub_group.group_account.primary_account_id in [1,2,5] else 2

    dr_sum = sum([e.amount for e in account.dr_entries])
    cr_sum = sum([e.amount for e in account.cr_entries])
    balance = dr_sum - cr_sum
    b_types = "D" if b_type == 2 and dr_sum > cr_sum else "C" if b_type == 1 and cr_sum > dr_sum else ""

    return {
        'id' : account.id,
        'balance' : abs(balance),
        'type' : b_types
    }

@acc_router.post("/group-account")
def add_group_account(group_account: GroupAccountsBase, session: Session=Depends(get_session)):
    try:
        new_group_account = create_group_account(
            group_account=group_account, session=session)
        session.add(new_group_account)
        session.commit()
        session.refresh(new_group_account)
        return new_group_account
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )


@acc_router.get("/group-account/{id}")
def read_group_account_by_id(id: int, session: Session=Depends(get_session)):
    group_account = session.get(GroupAccounts, id)
    if not group_account:
        raise HTTPException(
            status_code=404, detail=f"Group Account with id {id} does nt exits."
        )
    return group_account


@acc_router.post("/account")
def add_account(account: AccountsBase, session: Session=Depends(get_session)):
    try:
        new_account = create_account(account=account, session=session)
        session.add(new_account)
        session.commit()
        session.refresh(new_account)
        return new_account
    except Exception as e:
        raise HTTPException(
            status_code=403, detail=str(e)
        )


@acc_router.get("/account/{id}")
def read_account_by_id(id: int, session: Session=Depends(get_session)):
    account = session.get(Accounts, id)
    if not account:
        raise HTTPException(
            status_code=404, detail=f"Account with id {id} does not exist."
        )
    return account


@acc_router.get("/ledger/{id}")
def read_account_ledger(id: int, session: Session=Depends(get_session)):
    account = session.get(Accounts, id)

    if not account:
        raise HTTPException(
            status_code=404, detail=f"Account with id {id} does not exist.")

    debit = [
        {
            'account_name' : e.account.name,
            'amount' : e.amount if e.amount < entry.amount else entry.amount,
            'doc_date' : get_doc(e).doc_date,
            'doc' : get_doc(e).doc_prefix + str(get_doc(e).doc_number),
            'date_created' : e.date_created
        }for entry in account.dr_entries for e in entry.cr_entries
    ]
    credit = [
        {
            'account_name' : e.account.name,
            'amount' : e.amount if e.amount < entry.amount else entry.amount,
            'doc_date' : get_doc(e).doc_date,
            'doc' : get_doc(e).doc_prefix + str(get_doc(e).doc_number),
            'date_created' : e.date_created
        } for entry in account.cr_entries for e in entry.dr_entries
    ]

    dr_ledger = make_ledger(debit)
    cr_ledger = make_ledger(credit)

    return {
        'account': account,
        'debits': dr_ledger,
        'credits': cr_ledger
    }


@acc_router.get("/entries/{id}")
def read_account_entries(id:int, session:Session=Depends(get_session)):
    account = session.get(Accounts, id)
    if not account:
        raise HTTPException(
            status_code=404, detail=f"Account with id {id} does not exist."
        )
    return {
        'account' : account,
        'dr_entries' : account.dr_entries,
        'cr_entries' : account.cr_entries
    }