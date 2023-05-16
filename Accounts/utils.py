from typing import Union, List
from sqlmodel import Session, select
from database import get_engine
from Entries.models import DrEntries, CrEntries
from .models import Accounts, PrimaryAccounts, GroupAccounts, SubGroups
import os
import json

schema_dir = os.getcwd() + "/Accounts/schemas" 

def initialize_primary_accounts():
    with open(schema_dir+'/primary_accounts.json', 'r') as f:
        with Session(get_engine()) as session:
            primaries = json.loads(f.read())["Primary"]
            for primary in primaries:
                existing_p_account = session.exec(select(PrimaryAccounts).where(PrimaryAccounts.name==primary["name"])).first()
                if not existing_p_account:
                    new_p_account = PrimaryAccounts(name=primary.get("name"), id=primary.get("id"))
                    session.add(new_p_account)
                    session.commit()
    print("Finished Initializing Primary Accounts")

def initialize_group_accounts():
    with open(schema_dir + '/group_accounts.json', 'r') as f:
        with Session(get_engine()) as session:
            groups = json.loads(f.read())
            categories = [
                groups["Equities"],
                groups["Liabilities"],
                groups["Assets"],
                groups["Expenses"],
                groups["Revenue"],
            ]
            for category in categories:
                for g in category:
                    existing_account = session.exec(
                        select(GroupAccounts).where(
                            GroupAccounts.name == g["name"]
                        )
                    ).first()
                    if not existing_account:
                        new_g_account = GroupAccounts(
                            id=g["id"],
                            name=g["name"],
                            primary_account_id=g["primary_account_id"]
                        )
                        session.add(new_g_account)
                        session.commit()
    print("Finished Initializing Group Accounts")

def initialize_sub_groups():
    with open(schema_dir + '/subgroup.json', 'r') as f:
        with Session(get_engine()) as session:
            subs = json.loads(f.read()) ['SubGroups']
            for sub in subs:
                existing_sub = session.exec(select(SubGroups).where(SubGroups.name == sub["name"])).first()
                if not existing_sub:
                    new_sub = SubGroups(
                        id=sub["id"],
                        name=sub["name"],
                        group_account_id=sub["group_account_id"],
                    )
                    session.add(new_sub)
                    session.commit()
    print("Finished Initiallizing Sub Groups")

def initialize_accounts():
    with open(schema_dir + '/accounts.json', 'r') as f:
        with Session(get_engine()) as session:
            accounts = json.loads(f.read())["Accounts"]
            for account in accounts:
                existing_account = session.exec(select(Accounts).where(Accounts.name==account["name"])).first()
                if not existing_account:
                    new_account = Accounts(
                        id=account["id"],
                        name=account["name"],
                        sub_group_id=account["sub_group_id"]
                    )
                    session.add(new_account)
                    session.commit()
    print("Finished Initializing Accounts")

def get_doc(entry:Union[DrEntries, CrEntries]):
    
    if entry.journal:
        return entry.journal
    
    if entry.sales_invoice:
        return entry.sales_invoice
    
    if entry.purchase_invoice:
        return entry.purchase_invoice
    
    if entry.sales_return_voucher:
        return entry.sales_return_voucher
    
    if entry.purchase_return_voucher:
        return entry.purchase_return_voucher

def make_ledger(data):
    list_of_dictionaries_with_different_keys = {}
    for dictionary in data:
        key = (dictionary['account_name'], dictionary['doc'])
        if key in list_of_dictionaries_with_different_keys:
            list_of_dictionaries_with_different_keys[key]['amount'] += dictionary['amount']
        else:
            list_of_dictionaries_with_different_keys[key] = dictionary.copy()
    return list(list_of_dictionaries_with_different_keys.values())