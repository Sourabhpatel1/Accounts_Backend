from sqlmodel import Session, select
from .models import Accounts, AccountsBase, GroupAccountsBase, GroupAccounts, PrimaryAccounts, SubGroupBase, SubGroups

def create_group_account(group_account:GroupAccountsBase ,session:Session) -> GroupAccounts:
    primary_account = session.get(PrimaryAccounts, group_account.primary_account_id)
    
    if not primary_account:
        raise ValueError(f"Primary Account with id {group_account.primary_account_id} not found.")
    
    group_accounts = primary_account.group_accounts
    new_id = int(str(primary_account.id) + str(len(group_accounts)))
    
    new_group_account = GroupAccounts(
        id=new_id,
        name=group_account.name,
        primary_account_id=primary_account.id,
        primary_account=primary_account
    )

    return new_group_account

def create_sub_group(sub:SubGroupBase, session:Session) -> SubGroups:
    existing_sub_group = session.exec(select(SubGroups).where(SubGroups.name == sub.name)).first()
    if existing_sub_group:
        raise ValueError(f"A Sub Group with name {sub.name} already exists.")
    
    group = session.get(GroupAccounts, sub.group_account_id)

    if not group:
        raise ValueError(f"Group Account with id {sub.group_account_id} for creating Sub Group does not exist.")
    
    sub_groups = group.sub_groups

    new_id = int(str(str(group.id) + str(len(sub_groups))))

    new_sub_group = SubGroups(
        id=new_id,
        name=sub.name,
        group_account_id=group.id,
        group_account=group
    )
    return new_sub_group

def create_account(account:AccountsBase, session:Session) -> Accounts:

    existing_account = session.exec(select(Accounts).where(Accounts.name == account.name)).first()

    if existing_account:
        raise ValueError(f"Account with name {account.name} already exists.")

    sub_group = session.get(SubGroups, account.sub_group_id)
    
    if not sub_group:
        raise ValueError(f"Sub Group Account with id {account.group_account_id} for creating new account not found.")
    
    accounts = sub_group.accounts
    new_id = int(str(sub_group.id) + str(len(accounts)))

    new_account = Accounts(
        id=new_id,
        name=account.name,
        sub_group_id=sub_group.id,
        sub_group=sub_group
    )
    return new_account

