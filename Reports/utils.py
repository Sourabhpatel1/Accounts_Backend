from time import strptime
from datetime import date
from typing import Union

from Accounts.models import PrimaryAccounts, GroupAccounts, SubGroups
from Entries.models import DrEntries, CrEntries
from Accounts.utils import get_doc

def get_financial_year(fy_start:str, fy_end:str, next_year:bool) -> tuple:
    
    start_day = int(fy_start.split("-")[0])
    end_day = int(fy_end.split("-")[0])
    start_month = strptime(fy_start.split("-")[1], '%b').tm_mon
    end_month = strptime(fy_end.split("-")[1], '%b').tm_mon

    prev_start_year:int = None
    current_start_year:int = None

    previous_end_year:int = None
    current_end_year:int = None 

    if (date.today().month <= end_month and next_year):
        
        current_start_year = date.today().year - 1
        current_end_year = date.today().year

        prev_start_year = current_start_year - 1
        prev_start_year = current_end_year - 1
    else:
        current_start_year = date.today().year
        current_end_year = date.today().year + 1

        prev_start_year = current_start_year - 1
        previous_end_year = current_end_year - 1

    current_start_date = date(year=current_start_year, month=start_month, day=start_day)
    current_end_date = date(year=current_end_year, month=end_month, day=end_day)

    previous_start_date = date(year=prev_start_year, month=start_month, day=start_day)
    previous_end_date = date(year=previous_end_year, month=end_month, day=end_day)

    return current_start_date, current_end_date, previous_start_date, previous_end_date

def get_sheet(p:PrimaryAccounts, start:date, end:date):
    sheet = {}
    for g in p.group_accounts:
        sheet[g.name] = {}
        for s in g.sub_groups:
            sheet[g.name][s.name] = {}
            for a in s.accounts:
                b_type = 1 if a.sub_group.group_account.primary_account_id in [1,2,5] else 2
                dr_sum = sum([e.amount for e in a.dr_entries])
                cr_sum = sum([e.amount for e in a.cr_entries])
                balance = dr_sum - cr_sum
                b_types = "D" if b_type == 2 and dr_sum > cr_sum else "C" if b_type == 1 and cr_sum > dr_sum else ""
                sheet[g.name][s.name][a.name] = {
                    'balance' : abs(balance),
                    'type' : b_types
                }
    return sheet


def get_revenue_expense(revenue:PrimaryAccounts, expense:PrimaryAccounts):
    revenue_accounts = [a for g in revenue.group_accounts for s in g.sub_groups for a in s.accounts]
    expense_accounts = [a for g in expense.group_accounts for s in g.sub_groups for a in s.accounts]

    total_revenue_dr = sum([e.amount for a in revenue_accounts for e in a.dr_entries])
    total_revenue_cr = sum([e.amount for a in revenue_accounts for e in a.cr_entries])

    revenue = total_revenue_cr - total_revenue_dr

    total_expense_dr = sum([e.amount for a in expense_accounts for e in a.dr_entries])
    total_expense_cr = sum([e.amount for a in expense_accounts for e in a.cr_entries])

    expense = total_expense_dr - total_expense_cr

    return revenue, expense

def get_statement_values(
        start:str, 
        end:str, 
        next:bool,
        direct_expenses:GroupAccounts,
        operating_expenses:GroupAccounts,
        indirect_expenses:GroupAccounts,
        taxes_paid:GroupAccounts,
        direct_revenue:GroupAccounts,
        indirect_revenue:GroupAccounts,
        tax_benefits:GroupAccounts
    ) -> tuple:

    current_start, current_end, prev_start, prev_end = get_financial_year(start, end, next)

    def filter_entry(entry:Union[DrEntries, CrEntries]):
        date = entry.journal.doc_date if entry.journal else \
               entry.purchase_invoice.doc_date if entry.purchase_invoice else \
               entry.sales_invoice.doc_date if  entry.sales_invoice else entry.date_created

        if current_start <= date <= current_end:
            return True
        
        return False
    
    direct_ex_entry = [
            {
                'name' : account.name,
                'dr_entries' : [e for e in filter(filter_entry, account.dr_entries)],
                'cr_entries' : [e for e in filter(filter_entry, account.cr_entries)]
            } for s in direct_expenses.sub_groups for account in s.accounts
        ]
    
    
    operating_ex_entry = [
            {
                'name' : account.name,
                'dr_entries' : [e for e in filter(filter_entry, account.dr_entries)],
                'cr_entries' : [e for e in filter(filter_entry, account.cr_entries)]
            } for s in operating_expenses.sub_groups for account in s.accounts
        ]
    
    indirect_ex_entry = [
            {
                'name' : account.name,
                'dr_entries' : [e for e in filter(filter_entry, account.dr_entries)],
                'cr_entries' : [e for e in filter(filter_entry, account.cr_entries)]
            } for s in indirect_expenses.sub_groups for account in s.accounts
        ]
    tax_ex_entries = [
            {
                'name' : account.name,
                'dr_entries' : [e for e in filter(filter_entry, account.dr_entries)],
                'cr_entries' : [e for e in filter(filter_entry, account.cr_entries)]
            } for s in taxes_paid.sub_groups for account in s.accounts
        ]

    direct_rev_entry = [
            {
                'name' : account.name,
                'dr_entries' : [e for e in filter(filter_entry, account.dr_entries)],
                'cr_entries' : [e for e in filter(filter_entry, account.cr_entries)]
            } for s in direct_revenue.sub_groups for account in s.accounts
        ] 
    
    indirect_rev_entry = [
            {
                'name' : account.name,
                'dr_entries' : [e for e in filter(filter_entry, account.dr_entries)],
                'cr_entries' : [e for e in filter(filter_entry, account.cr_entries)]
            } for s in indirect_revenue.sub_groups for account in s.accounts
        ]
    
    tax_rev_entry = [
            {
                'name' : account.name,
                'dr_entries' : [e for e in filter(filter_entry, account.dr_entries)],
                'cr_entries' : [e for e in filter(filter_entry, account.cr_entries)]
            } for s in tax_benefits.sub_groups for account in s.accounts
    ]
    
    return (direct_ex_entry, operating_ex_entry, indirect_ex_entry, tax_ex_entries, direct_rev_entry, indirect_rev_entry, tax_rev_entry)


def get_net_profit(revenues:PrimaryAccounts, expenses:PrimaryAccounts, start:date, end:date):
    total_revenue = sum([e.amount for g in revenues.group_accounts for s in g.sub_groups for a in s.accounts for e in a.cr_entries if start <= get_doc(e).doc_date <= end])  - \
                    sum([e.amount for g in revenues.group_accounts for s in g.sub_groups for a in s.accounts for e in a.dr_entries if start <= get_doc(e).doc_date <= end])

    total_expenses = sum([e.amount for g in expenses.group_accounts for s in g.sub_groups for a in s.accounts for e in a.dr_entries if start <= get_doc(e).doc_date <= end]) - \
                     sum([e.amount for g in expenses.group_accounts for s in g.sub_groups for a in s.accounts for e in a.cr_entries if start <= get_doc(e).doc_date <= end])

    net_profit = total_revenue - total_expenses

    return net_profit

def get_cah_flow_adjustments(d:SubGroups, start:date, end:date):
    non_cash = []
    for a in d.accounts:
        non_cash.append({
            'name' : a.name,
            'change' : sum([e.amount for e in a.dr_entries]) - sum([e.amount for e in a.cr_entries])
        })
    return non_cash

def get_working_capital_changes(cl:GroupAccounts, ca:GroupAccounts, start:date, end:date):
    change_in_cl = []
    for s in cl.sub_groups:
        if not s.id == 213:
            cr = sum([e.amount for a in s.accounts for e in a.cr_entries if start <= get_doc(e).doc_date <= end])
            dr = sum([e.amount for a in s.accounts for e in a.dr_entries if start <= get_doc(e).doc_date <= end])

            sub = {
                'name' : s.name,
                'change' : cr - dr
            }
            change_in_cl.append(sub)
    
    change_in_ca = []
    for s in ca.sub_groups:
        if not s.id in [321]:
            cr = sum([e.amount for a in s.accounts for e in a.cr_entries if start <= get_doc(e).doc_date <= end])
            dr = sum([e.amount for a in s.accounts for e in a.dr_entries if start <= get_doc(e).doc_date <= end])

            sub = {
                'name' : s.name,
                'change' : dr - cr
            }
            change_in_ca.append(sub)


    return change_in_cl, change_in_ca

def get_taxes_paid(tax:GroupAccounts, start:date, end:date):
    tax_paid = []
    for s in tax.sub_groups:
        cr = sum([e.amount for a in s.accounts for e in a.cr_entries if start <= get_doc(e).doc_date <= end])
        dr = sum([e.amount for a in s.accounts for e in a.dr_entries if start <= get_doc(e).doc_date <= end])

        sub = {
            'name' : s.name,
            'change' : dr - cr
        }
        tax_paid.append(sub)
    return tax_paid

def get_change_in_investmenst(assets:GroupAccounts, inv:GroupAccounts, interest:SubGroups, div:SubGroups, start:date, end:date):
    change_in_a = []
    for s in assets.sub_groups:
        cr = sum([e.amount for a in s.accounts for e in a.cr_entries if start <= get_doc(e).doc_date <= end])
        dr = sum([e.amount for a in s.accounts for e in a.dr_entries if start <= get_doc(e).doc_date <= end])

        sub = {
            'name' : s.name,
            'change' : dr - cr
        }
        change_in_a.append(sub)
    
    for s in inv.sub_groups:
        cr = sum([e.amount for a in s.accounts for e in a.cr_entries if start <= get_doc(e).doc_date <= end])
        dr = sum([e.amount for a in s.accounts for e in a.dr_entries if start <= get_doc(e).doc_date <= end])

        sub = {
            'name' : s.name,
            'change' : dr - cr
        }
        change_in_a.append(sub)
    
    for a in interest.accounts:
        cr = sum([e.amount for e in a.cr_entries if start <= get_doc(e).doc_date <= end])
        dr = sum([e.amount for e in a.dr_entries if start <= get_doc(e).doc_date <= end])

        sub = {
            'name' : s.name,
            'change' : dr - cr
        }
        change_in_a.append(sub)

    for a in div.accounts:
        cr = sum([e.amount for e in a.cr_entries if start <= get_doc(e).doc_date <= end])
        dr = sum([e.amount for e in a.dr_entries if start <= get_doc(e).doc_date <= end])

        sub = {
            'name' : s.name,
            'change' : dr - cr
        }
        change_in_a.append(sub)  
    return change_in_a

def get_change_in_fa(ip:SubGroups, dp:SubGroups, l:GroupAccounts, e:SubGroups, start:date, end:date):
    change_in_fa = []
    for a in e.accounts:
        cr = sum([e.amount for e in a.cr_entries if start <= get_doc(e).doc_date <= end])
        dr = sum([e.amount for e in a.dr_entries if start <= get_doc(e).doc_date <= end])

        change_in_fa.append({
            'name' : a.name,
            'change' : cr - dr
        })
    for a in ip.accounts:
        cr = sum([e.amount for e in a.cr_entries if start <= get_doc(e).doc_date <= end])
        dr = sum([e.amount for e in a.dr_entries if start <= get_doc(e).doc_date <= end])

        sub = {
            'name' : a.name,
            'change' : dr - cr
        }
        change_in_fa.append(sub)

    for a in dp.accounts:   
        cr = sum([e.amount for e in a.cr_entries if start <= get_doc(e).doc_date <= end])
        dr = sum([e.amount for e in a.dr_entries if start <= get_doc(e).doc_date <= end])

        sub = {
            'name' : a.name,
            'change' : cr - dr
        }
        change_in_fa.append(sub)

    for s in l.sub_groups:
        cr = sum([e.amount for a in s.accounts for e in a.cr_entries if start <= get_doc(e).doc_date <= end])
        dr = sum([e.amount for a in s.accounts for e in a.dr_entries if start <= get_doc(e).doc_date <= end])

        sub = {
            'name' : s.name,
            'change' : cr - dr
        }
        change_in_fa.append(sub)

    return change_in_fa

def get_cash_balances(cash:SubGroups, c_start, c_end, p_start, p_end):
    opening = []
    closing = []
    for a in cash.accounts:
        opening.append({
            'name' : a.name,
            'balance' : sum([e.amount for e in a.dr_entries if get_doc(e).doc_date <= c_start]) - sum([e.amount for e in a.cr_entries if get_doc(e).doc_date <= c_start])
        })
        closing.append({
            'name' : a.name,
            'balance' : sum([e.amount for e in a.dr_entries if c_start <= get_doc(e).doc_date <= c_end]) - sum([e.amount for e in a.cr_entries if c_start <= get_doc(e).doc_date <= c_end])
        })
    return opening, closing
