from typing import List
from sqlmodel import Session
from .models import JournalBase, Journals
from Entries.models import DrEntries, CrEntries, EntryType
from Entries.crud import create_dr_entry, create_cr_entry

def create_journal(journal:JournalBase, master_entry_type:EntryType):
    try:
        new_journal = Journals.from_orm(journal, update={'master_entry_type':master_entry_type})
        return new_journal
    except Exception as e:
        print(e)
        raise ValueError(f"Journal could not be created")

def cancel_journal(id:int, session:Session):
    journal = session.get(Journals, id)

    if not journal: 
        raise ValueError(f"Journal with id {id} does not exist.")

    if not journal.status:
        raise ValueError(f"Journal with id {id} is already cancelled")
    
    journal.status = False

    master_entry = journal.dr_entries[0] if journal.master_entry_type == EntryType.Debit else journal.cr_entries[0] if journal.master_entry_type == EntryType.Credit else None

    if not master_entry:
        raise ValueError(f"Journal with id {id} is already cancelled")

    if journal.master_entry_type == EntryType.Debit:
        print("Master Entry Debit")
        
        new_entries:List[DrEntries] = []
        
        for entry in journal.cr_entries:
            reverse_entry = create_dr_entry(account=entry.account, journal=journal, amount=entry.amount)
            new_entries.append(reverse_entry)
        
        reverse_master_entry = create_cr_entry(account=master_entry.account, journal=journal, amount=master_entry.amount)
        
        for entry in new_entries:
            entry.cr_entries.append(reverse_master_entry)
            session.add(entry)

    if journal.master_entry_type == EntryType.Credit:
        print("Master Entry Credit")
        new_entries:List[CrEntries] = []
        for entry in journal.dr_entries:
            reverse_entry = create_cr_entry(account=entry.account, journal=journal, amount=entry.amount)
            new_entries.append(reverse_entry)

        reverse_master_entry =  create_dr_entry(account=master_entry.account, journal=master_entry.journal, amount=master_entry.amount)

        for entry in new_entries:
            entry.dr_entries.append(reverse_master_entry)
            session.add(entry)

    session.add(journal)

    return journal