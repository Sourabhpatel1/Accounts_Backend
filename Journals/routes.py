from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from Accounts.models import Accounts
from Entries.models import EntriesRequest, MasterEntryRequest, DrEntries, CrEntries, EntryType
from Entries.crud import create_dr_entry, create_cr_entry
from .models import JournalBase, Journals
from .crud import create_journal, cancel_journal

journal_router = APIRouter(prefix="/journal", tags=["Journals"])

@journal_router.get("/")
def read_all_jornals(session:Session=Depends(get_session)):
    journals = session.exec(select(Journals)).all()
    return [
        {
            'journal' : journal,
            'dr_entries' : journal.dr_entries,
            'cr_entries' : journal.cr_entries
        } for journal in journals
    ]

@journal_router.get("/{id}")
def read_journal_by_id(id:int, session:Session=Depends(get_session)):
    journal = session.get(Journals, id)
    if not journal:
        raise HTTPException(
            status_code=404, detail=f"Jurnal with id {id} does not exist."
        )
    return {
        'journal' : journal,
        'dr_entries' : [
            {
                'account_name' : entry.account.name,
                'amount' : entry.amount
            } for entry in journal.dr_entries
        ],
        'cr_entries' : [
            {
                'account_name' : entry.account.name,
                'amount' : entry.amount
            } for entry in journal.cr_entries
        ]
    }

@journal_router.post("/")
def add_new_journal(journal:JournalBase, master_entry:MasterEntryRequest, entries:List[EntriesRequest], session:Session=Depends(get_session)):
    master_account = session.get(Accounts, master_entry.account_id)
    if not master_account:
        raise HTTPException(
            status_code = 404, detail=f"Account with id {master_entry.account_id} does not exist."
        )
    try:
        new_journal = create_journal(journal=journal, master_entry_type=master_entry.entry_type)
        session.add(new_journal)

        if master_entry.entry_type == EntryType.Debit:
            new_master_entry = create_dr_entry(journal=new_journal, account=master_account, amount=master_entry.amount)
            session.add(new_master_entry)
            for entry in entries:
                account = session.get(Accounts, entry.account_id)
                if not account:
                    raise HTTPException(
                        status_code = 404, detail=f"Account with id {master_entry.account_id} does not exist."
                    )       
                new_entry = create_cr_entry(journal=new_journal, account=account, amount=entry.amount)
                session.add(new_entry)
                new_master_entry.cr_entries.append(new_entry)
                session.add(new_master_entry)

        if master_entry.entry_type == EntryType.Credit:
            new_master_entry = create_cr_entry(journal=new_journal, account=master_account, amount=master_entry.amount)
            session.add(new_master_entry)
            for entry in entries:
                account = session.get(Accounts, entry.account_id)
                if not account:
                    raise HTTPException(
                        status_code = 404, detail=f"Account with id {master_entry.account_id} does not exist."
                    )       
                new_entry = create_dr_entry(journal=new_journal, account=account, amount=entry.amount)
                session.add(new_entry)
                new_master_entry.dr_entries.append(new_entry)
                session.add(new_master_entry)
        session.add(new_journal)
        session.commit()
        session.refresh(new_journal)
        return {
            "journal" : new_journal,
            "dr_entries" : new_journal.dr_entries, 
            "cr_entries" : new_journal.cr_entries 
        }
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=403, detail=f"Error : {str(e)}"
        )

@journal_router.delete("/{id}")
def delete_journal(id:int, session:Session=Depends(get_session)):
    try:
        cancelled_journal = cancel_journal(id=id, session=session)
        session.commit()
        session.refresh(cancelled_journal)
        return {
            ' journal' : cancelled_journal,
            'dr_entries' : cancelled_journal.dr_entries,
            'cr_entries' : cancelled_journal.cr_entries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))