from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session, get_company_session

from Business.models import Business
from Accounts.models import PrimaryAccounts, GroupAccounts, Accounts, SubGroups
from Accounts.utils import get_doc

from .utils import (
        get_financial_year, 
        get_sheet, 
        get_revenue_expense,
        get_statement_values,
        get_net_profit,
        get_cah_flow_adjustments,
        get_working_capital_changes,
        get_taxes_paid,
        get_change_in_investmenst,
        get_change_in_fa,
        get_cash_balances
    )

reports_router = APIRouter(prefix="/reports", tags=["Reports"])

@reports_router.get("/balance_sheet")
def read_balance_sheet(session:Session=Depends(get_session), company_session:Session=Depends(get_company_session)):
    business = company_session.exec(select(Business).where(Business.is_active)).first()
    
    equity = session.get(PrimaryAccounts, 1)
    liabilities = session.get(PrimaryAccounts, 2)
    assets = session.get(PrimaryAccounts, 3)
    expenses = session.get(PrimaryAccounts, 4)
    revenue = session.get(PrimaryAccounts, 5)

    current_start, current_end, prev_start, prev_end = get_financial_year(business.fy_start, business.fy_end, business.next_year)

    equity_sheet = get_sheet(equity, start=current_start, end=current_end)
    liabilities_sheet = get_sheet(liabilities, start=current_start, end=current_end)
    assets_sheet = get_sheet(assets, start=current_start, end=current_end)
    
    total_revenue, total_expense = get_revenue_expense(revenue=revenue, expense=expenses)

    return  {
        'balance_sheet' : {
            'equity' : equity_sheet,
            'liabilities' : liabilities_sheet,
            'assets' : assets_sheet
        },
        'revenue' : total_revenue,
        'expense' : total_expense,
        'current_start' : current_start,
        'current_end' : current_end,
        'previous_start' : prev_start,
        'previous_end' : prev_end
    }

@reports_router.get("/profit_and_loss")
def read_profit_and_loss_statement(session:Session=Depends(get_session), company_session:Session=Depends(get_company_session)):
    business = company_session.exec(select(Business).where(Business.is_active)).first()
    
    direct_expenses = session.get(GroupAccounts, 40)
    operating_expenses = session.get(GroupAccounts, 41)
    indirect_expenses = session.get(GroupAccounts, 42)
    tax_expenses = session.get(GroupAccounts, 43)

    direct_revenue = session.get(GroupAccounts, 50)
    indirect_revenue = session.get(GroupAccounts, 51)
    tax_income = session.get(GroupAccounts, 52)

    direct_expense, \
    operating_expenses, \
    indirect_expense, \
    tax_paid, \
    direct_income, \
    indirect_income, \
    tax_refund = get_statement_values(
        direct_expenses=direct_expenses,
        operating_expenses=operating_expenses,
        indirect_expenses=indirect_expenses,
        taxes_paid=tax_expenses,
        direct_revenue=direct_revenue,
        indirect_revenue=indirect_revenue,
        tax_benefits=tax_income,
        start=business.fy_start,
        end=business.fy_end,
        next=business.next_year
    )

    return  {
                'direct_revenue' : direct_income,
                'indirect_revenue' : indirect_income,
                'direct_expenses' : direct_expense,
                'operating_expenses' : operating_expenses,
                'indirect_expenses' : indirect_expense,
                'tax_expenses' : tax_paid,
                'tax_income' : tax_refund
            }
    
@reports_router.get("/cash_flow")
def read_cash_flow(session:Session=Depends(get_session), company_session:Session=Depends(get_company_session)):
    business = company_session.exec(select(Business).where(Business.is_active)).first()
    
    cash_equi = session.get(SubGroups, 321)

    equity = session.get(SubGroups, 100)

    revenues = session.get(PrimaryAccounts, 5)
    expenses = session.get(PrimaryAccounts, 4)

    depriciation = session.get(SubGroups, 413)

    current_liabilities = session.get(GroupAccounts, 21)
    current_assets = session.get(GroupAccounts, 32)

    assets = session.get(GroupAccounts, 30)
    investments = session.get(GroupAccounts, 31)

    interest = session.get(SubGroups, 512)
    dividents = session.get(SubGroups, 513)

    interest_paid = session.get(SubGroups, 424)
    divident_payable = session.get(SubGroups, 213)
    liabilities = session.get(GroupAccounts, 20)

    tax = session.get(GroupAccounts, 43)


    current_start, current_end, prev_start , prev_end = get_financial_year(
        fy_start=business.fy_start,
        fy_end=business.fy_end,
        next_year=business.next_year
    )
    # Net Profit
    net_profit = get_net_profit(revenues=revenues, expenses=expenses, start=current_start, end=current_end)
    
    # Adjustments
    adjusments = get_cah_flow_adjustments(depriciation, start=current_start, end=current_end)

    # working capital changes
    change_in_cl, change_in_ca = get_working_capital_changes(ca=current_assets, cl=current_liabilities, start=current_start, end=current_end)

    # Income Tax
    tax_paid = get_taxes_paid(tax=tax, start=current_start, end=current_end)    

    #Assets and Investment
    investing_activities = get_change_in_investmenst(assets=assets, inv=investments, interest=interest, div=dividents, start=current_start, end=current_end)
    
    #Financing Activity
    financing_activities = get_change_in_fa(ip=interest_paid, dp=divident_payable, l=liabilities, e=equity, start=current_start, end=current_end)


    opening_cash, closing_cash = get_cash_balances(cash=cash_equi, c_start=current_start, c_end=current_end, p_start=prev_start, p_end=prev_end)

    return {
        'net_profit' : net_profit,
        'change_in_cl' : change_in_cl,
        'change_in_ca' : change_in_ca,
        'non_cash' : adjusments,
        'tax_paid' : tax_paid,
        'investment' : investing_activities,
        'financing' : financing_activities,
        'opening_cash' : opening_cash,
        'closing_cash' : closing_cash
    }