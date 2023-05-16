from itertools import groupby
from datetime import date
from sqlmodel import Session, select
from Accounts.models import PrimaryAccounts, GroupAccounts, SubGroups, Accounts
from Accounts.utils import get_doc
from Reports.utils import get_net_profit
from PurchaseDocs.models import PurchaseInvoices, PurchaseOrders
from SalesDocs.models import SalesInvoices, SalesOrders
from Customers.models import Customers
from Vendors.models import Vendors


def get_current_ratio(start:date, end:date, session:Session):
    current_assets = session.get(GroupAccounts, 32)
    current_liabilities = session.get(GroupAccounts, 21)

    ca_dr_value = sum([e.amount for s in current_assets.sub_groups for a in s.accounts for e in a.dr_entries if start <= get_doc(e).doc_date <= end])
    ca_cr_value = sum([e.amount for s in current_assets.sub_groups for a in s.accounts for e in a.cr_entries if start <= get_doc(e).doc_date <= end])

    cl_dr_value = sum([e.amount for s in current_liabilities.sub_groups for a in s.accounts for e in a.dr_entries if start <= get_doc(e).doc_date <= end])
    cl_cr_value = sum([e.amount for s in current_liabilities.sub_groups for a in s.accounts for e in a.cr_entries if start <= get_doc(e).doc_date <= end])

    total_ca = ca_dr_value - ca_cr_value
    total_cl = cl_cr_value - cl_dr_value

    if total_cl == 0:
        total_cl = 1

    return round(total_ca / total_cl, 2)

def get_cash_ratio(start:date, end:date, session:Session):
    cash = session.get(SubGroups, 321)
    current_liabilities = session.get(GroupAccounts, 21)
    
    cash_dr = sum([e.amount for a in cash.accounts for e in a.dr_entries if start <= get_doc(e).doc_date <= end])
    cash_cr = sum([e.amount for a in cash.accounts for e in a.cr_entries if start <= get_doc(e).doc_date <= end])

    cl_dr_value = sum([e.amount for s in current_liabilities.sub_groups for a in s.accounts for e in a.dr_entries if start <= get_doc(e).doc_date <= end])
    cl_cr_value = sum([e.amount for s in current_liabilities.sub_groups for a in s.accounts for e in a.cr_entries if start <= get_doc(e).doc_date <= end])

    total_cash = cash_dr - cash_cr
    total_cl = cl_cr_value - cl_dr_value
    
    if total_cl == 0:
        total_cl = 1
    
    return round(total_cash / total_cl)

def get_profit_ratios(start:date, end:date, session:Session):
    revenue_sales = session.get(SubGroups, 500)
    revenue_service = session.get(SubGroups, 501)
    
    cogs = session.get(SubGroups, 400)
    cost_of_service = session.get(SubGroups, 401)
    operating_expenses = session.get(GroupAccounts, 41)

    revenue = session.get(PrimaryAccounts, 5)
    expenses = session.get(PrimaryAccounts, 4)

    sales_dr = sum([e.amount for a in revenue_sales.accounts for e in a.dr_entries if start<=get_doc(e).doc_date<=end])
    sales_cr = sum([e.amount for a in revenue_sales.accounts for e in a.cr_entries if start<=get_doc(e).doc_date<=end])

    service_dr = sum([e.amount for a in revenue_service.accounts for e in a.dr_entries if start<=get_doc(e).doc_date<=end])
    service_cr = sum([e.amount for a in revenue_service.accounts for e in a.cr_entries if start<=get_doc(e).doc_date<=end])

    revenue_dr = sum([e.amount for g in revenue.group_accounts for s in g.sub_groups for a in s.accounts for e in a.dr_entries if start<=get_doc(e).doc_date<=end])
    revenue_cr = sum([e.amount for g in revenue.group_accounts for s in g.sub_groups for a in s.accounts for e in a.cr_entries if start<=get_doc(e).doc_date<=end])

    cogs_dr = sum([e.amount for a in cogs.accounts for e in a.dr_entries if start<=get_doc(e).doc_date<=end])
    cogs_cr = sum([e.amount for a in cogs.accounts for e in a.cr_entries if start<=get_doc(e).doc_date<=end])

    cost_service_dr = sum([e.amount for a in cost_of_service.accounts for e in a.dr_entries if start<=get_doc(e).doc_date<=end])
    cost_service_cr = sum([e.amount for a in cost_of_service.accounts for e in a.cr_entries if start<=get_doc(e).doc_date<=end])

    operating_dr = sum([e.amount for s in operating_expenses.sub_groups for a in s.accounts for e in a.dr_entries if start<=get_doc(e).doc_date<=end])
    operating_cr = sum([e.amount for s in operating_expenses.sub_groups for a in s.accounts for e in a.cr_entries if start<=get_doc(e).doc_date<=end])

    expenses_dr = sum([e.amount for g in expenses.group_accounts for s in g.sub_groups for a in s.accounts for e in a.dr_entries if start<=get_doc(e).doc_date<=end])
    expenses_cr = sum([e.amount for g in expenses.group_accounts for s in g.sub_groups for a in s.accounts for e in a.cr_entries if start<=get_doc(e).doc_date<=end])

    direct_revenue_sum = sales_cr + service_cr - sales_dr - service_dr

    cogs_sum = cogs_dr + cost_service_dr - cogs_cr - cost_service_cr
    operating_expenses_sum = operating_dr - operating_cr

    gross_profit = direct_revenue_sum - cogs_sum
    operating_profit = gross_profit - operating_expenses_sum
    net_profit = revenue_cr + expenses_cr - revenue_dr - expenses_dr
    
    try:
        gross_margin = round(gross_profit/direct_revenue_sum, 2)
        operating_margin = round(operating_profit / direct_revenue_sum, 2)
        net_margin = round(net_profit/direct_revenue_sum, 2)
    except ZeroDivisionError:
        gross_margin = 0
        operating_margin = 0
        net_margin = 0


    return {
        "Gross Margin" : gross_margin,
        "Operating Margin" : operating_margin,
        "Net Margin" : net_margin
    }

    
def get_debt_ratios(start:date, end:date, session:Session):
    liabilities = session.get(PrimaryAccounts, 2)
    equity = session.get(PrimaryAccounts, 1)
    assets = session.get(PrimaryAccounts, 3)

    liabilities_dr = sum([e.amount for g in liabilities.group_accounts for s in g.sub_groups for a in s.accounts for e in a.dr_entries if start<=get_doc(e).doc_date<=end])
    liabilities_cr = sum([e.amount for g in liabilities.group_accounts for s in g.sub_groups for a in s.accounts for e in a.cr_entries if start<=get_doc(e).doc_date<=end])

    equities_dr = sum([e.amount for g in equity.group_accounts for s in g.sub_groups for a in s.accounts for e in a.dr_entries if start<=get_doc(e).doc_date<=end])
    equities_cr = sum([e.amount for g in equity.group_accounts for s in g.sub_groups for a in s.accounts for e in a.cr_entries if start<=get_doc(e).doc_date<=end])

    assets_dr = sum([e.amount for g in assets.group_accounts for s in g.sub_groups for a in s.accounts for e in a.dr_entries if start<=get_doc(e).doc_date<=end])
    assets_cr = sum([e.amount for g in assets.group_accounts for s in g.sub_groups for a in s.accounts for e in a.cr_entries if start<=get_doc(e).doc_date<=end])

    total_liabilities = liabilities_cr - liabilities_dr
    total_equity  = equities_cr - equities_dr
    total_assets = assets_dr - assets_cr
    
    net_profit = get_net_profit(revenues=session.get(PrimaryAccounts, 5), expenses=session.get(PrimaryAccounts, 4), start=start, end=end)

    try:
        dte_ratio = round(total_liabilities/total_equity if total_equity > 0 else 1, 2)
        debt_ratio = round(total_liabilities/total_assets if total_assets > 0 else 1, 2)
        return_on_equity = round(net_profit/total_equity, 2)
        return_on_asstes = round(net_profit/total_assets, 2)
    except ZeroDivisionError:
        dte_ratio = 0
        debt_ratio = 0
        return_on_equity = 0
        return_on_asstes = 0
        
    return {
        "Debt To Equity Ratio" : dte_ratio,
        "Debt Ratio" : debt_ratio,
        "ROE" : return_on_equity,
        "ROA" : return_on_asstes
    }

def get_sales_quantities(session:Session):
    sales_invoices = session.exec(select(SalesInvoices)).all()
    sold_quantities = {}
    for invoice in sales_invoices:
        for item in invoice.line_items:
            if not item.item.name in sold_quantities:
                sold_quantities[item.item.name] = item.quantity * item.price
            else:
                sold_quantities[item.item.name] += item.quantity * item.price
    return sold_quantities

def get_purchase_quantities(session:Session):
    p_inv = session.exec(select(PurchaseInvoices)).all()
    p_qty = {}
    for invoice in p_inv:
        for item in invoice.line_items:
            if not item.item.name in p_qty:
                p_qty[item.item.name] = item.quantity * item.price
            else:
                p_qty[item.item.name] += item.quantity * item.quantity
    return p_qty

def get_party_data(session:Session):
    customers = session.exec(select(Customers)).all()
    vendors = session.exec(select(Vendors)).all()

    customer_res = []
    vendor_res = []

    for c in customers:
        c_dict = {c.name : 0}
        for inv in c.s_invoices:
            for item in inv.line_items:
                c_dict[c.name] += item.price * item.quantity    
        customer_res.append(c_dict)
    
    for v in vendors:
        v_dict = {v.name : 0}
        for inv in v.p_invoices:
            for item in inv.line_items:
                v_dict[v.name] += item.price * item.quantity    
        vendor_res.append(v_dict)

    return customer_res, vendor_res

def get_cash_data(session:Session):
    cash_account = session.get(Accounts, 3210)
    bank_account = session.get(Accounts, 3211)

    cash_dr = [{"x" : get_doc(e).doc_date, "y" : e.amount} for e in cash_account.dr_entries]
    cash_cr = [{"x" : get_doc(e).doc_date, "y" : e.amount} for e in cash_account.cr_entries]
    bank_dr = [{"x" : get_doc(e).doc_date, "y" : e.amount} for e in bank_account.dr_entries]
    bank_cr = [{"x" : get_doc(e).doc_date, "y" : e.amount} for e in bank_account.cr_entries]
    
    g1 = groupby(sorted(cash_dr, key=lambda x : x["x"]), lambda x : x["x"])
    g2 = groupby(sorted(cash_cr, key=lambda x : x["x"]), lambda x : x["x"])
    g3 = groupby(sorted(bank_dr, key=lambda x : x["x"]), lambda x : x["x"])
    g4 = groupby(sorted(bank_cr, key=lambda x : x["x"]), lambda x : x["x"])
    
    cash_dr = [{"x" : k, "y" : sum(i["y"] for i in g)} for k, g in g1]
    cash_cr = [{"x" : k, "y" : sum(i["y"] for i in g)} for k, g in g2]
    bank_dr = [{"x" : k, "y" : sum(i["y"] for i in g)} for k, g in g3]
    bank_cr = [{"x" : k, "y" : sum(i["y"] for i in g)} for k, g in g4]

    return sorted(cash_dr, key=lambda x : x["x"]), sorted(cash_cr, key=lambda x : x["x"]), sorted(bank_dr, key=lambda x : x["x"]), sorted(bank_cr, key=lambda x : x["x"])
