from typing import Optional
from Accounts.models import Accounts
from Journals.models import Journals
from PurchaseDocs.models import PurchaseInvoices, PurchaseReturnVouchers
from SalesDocs.models import SalesInvoices, SalesReturnVouchers
from .models import DrEntries, CrEntries

def create_dr_entry(
        amount:float, 
        account:Accounts, 
        journal:Optional[Journals] = None, 
        si:Optional[SalesInvoices]=None, 
        pi:Optional[PurchaseInvoices] = None,
        prv:Optional[PurchaseReturnVouchers] = None,
        srv:Optional[SalesReturnVouchers] = None
    ):
    new_dr_entry = DrEntries(
        journal_id=journal.id if journal else None,
        purchase_invoice_id=pi.id if pi  else None,
        sales_invoice_id=si.id if si  else None,
        purchase_return_voucher_id=prv.id if prv else None,
        sales_return_voucher_id=srv.id if srv else None,
        account_id=account.id,
        amount=amount,
        journal=journal,
        purchase_invoice=pi,
        sales_invoice=si,
        purchase_return_voucher=prv,
        sales_return_voucher=srv,
        account=account
    )
    return new_dr_entry

def create_cr_entry(
        amount:float, 
        account:Accounts, 
        journal:Optional[Journals] = None, 
        si:Optional[SalesInvoices]=None, 
        pi:Optional[PurchaseInvoices] = None,
         prv:Optional[PurchaseReturnVouchers] = None,
        srv:Optional[SalesReturnVouchers] = None
    ):
    new_cr_entry = CrEntries(
        journal_id=journal.id if journal else None,
        purchase_invoice_id=pi.id if pi  else None,
        sales_invoice_id=si.id if si  else None,
        purchase_return_voucher_id=prv.id if prv else None,
        sales_return_voucher_id=srv.id if srv else None,
        account_id=account.id,
        journal=journal,
        purchase_invoice=pi,
        sales_invoice=si,
        account=account,
        purchase_return_voucher=prv,
        sales_return_voucher=srv,
        amount=amount
    )
    return new_cr_entry