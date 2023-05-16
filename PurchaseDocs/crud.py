from typing import Optional, List
from sqlmodel import Session, select
from field_types import TransactionTypes, StateType, DocumentTypes, OrderStatus
from Accounts.models import Accounts
from Entries.models import EntryType, MasterEntryRequest, EntriesRequest, CrEntries, DrEntries
from Entries.crud import create_dr_entry, create_cr_entry
from Inventory.models import InventoryItems, LineItemBase, POLineItems, PILineItems, PRLineItems, PRLineItemsBase, Stocks
from Journals.models import JournalBase, Journals
from Terms.models import PurchaseOrderTerms, PurchaseInvoiceTerms
from Vendors.models import Vendors
from .models import PurchaseOrderBase, PurchaseOrders, PurchaseInvoicesBase, PurchaseInvoices, PurchaseReturnVoucherBase, PurchaseReturnVouchers

def create_purhcase_order(order:PurchaseOrderBase, session:Session):
    vendor = session.get(Vendors, order.vendor_id)
    terms  = session.get(PurchaseOrderTerms, order.terms_id)
    if not vendor:
        raise ValueError(f"Vendor with id {order.vendor_id} does not exist.")

    new_po = PurchaseOrders(
        doc_date=order.doc_date, 
        doc_number=order.doc_number,
        state_type=order.state_type,
        terms_id=order.terms_id,
        terms=terms,
        vendor_id=vendor.id,
        vendor=vendor,
    )

    return new_po

def create_po_line_items(items:List[LineItemBase], po:PurchaseOrders, session:Session):
    for item in items:
       inventory = session.get(InventoryItems, item.item_id)
       if not inventory:
           raise ValueError(f"Item with id {item.item_id} does not exist.")
       new_line_item =  POLineItems.from_orm(
           item,
           update={
            'po_id' : po.id,
            'po' : po,
            'item' : item
           }
       )
       po.line_items.append(new_line_item)
    session.add(po)
    

def create_purchase_invoice(invoice:PurchaseInvoicesBase, session:Session):
    po = session.get(PurchaseOrders, invoice.po_id)
    po_vendor = session.get(Vendors, po.vendor_id) if po else None
    vendor = session.get(Vendors, invoice.vendor_id)

    if not vendor:
        raise ValueError(f"Vendor with id {invoice.vendor_id} does not exist.")

    if po_vendor and vendor:
        if po_vendor != vendor:
            raise ValueError("Can not issue purchase invoice to a diffrent vendor than purchase order vendor.")
    
    terms = session.get(PurchaseInvoiceTerms, invoice.terms_id)

    new_invoice = PurchaseInvoices(
        doc_date=invoice.doc_date,
        doc_number=invoice.doc_number,
        vendor_id=vendor.id,
        state_type=invoice.state_type,
        terms=terms,
        po_id=invoice.po_id,
        purchase_order=po,
        vendor=vendor,
        terms_id=invoice.terms_id,
        transaction_type=invoice.transaction_type,
        rounded_off=invoice.rounded_off
    )

    return new_invoice

def create_stock(item:InventoryItems, line_item:PILineItems):
    new_stock = Stocks(
        item_id=item.id,
        line_item_id=line_item.id,
        quantity=line_item.quantity,
        price=line_item.price,
        item=item,
        line_item=line_item
    )
    return new_stock

def create_purchase_invoice_line_items(items:List[LineItemBase], pi:PurchaseInvoices, session:Session):
    for item in items:
        inventory = session.get(InventoryItems, item.item_id)
        
        if pi.purchase_order:
            if inventory not in [l.item for l in pi.purchase_order.line_items]:
                raise ValueError(f"Item {inventory.name} is not a purchase order line item.")

            for po_item in pi.purchase_order.line_items:
                if po_item.item_id == item.item_id:
                    if po_item.quantity < item.quantity:
                        raise ValueError(f"Purchase quantity for item {po_item.item.name} is greater than purchase order quantity")

        if not inventory:
            raise ValueError(f"Item with id {item.item_id} does not exist.")
        
        new_line_item = PILineItems(
            item_id=inventory.id,
            item=inventory,
            price=item.price,
            quantity=item.quantity,
            discount_rate=item.discount_rate,
            discount_amount= (item.price * item.quantity) * item.discount_rate / 100,
            pi_id=pi.id,
            pi=pi,
        )
        
        new_stock = create_stock(item=inventory, line_item=new_line_item)
        session.add(new_stock)
    
    session.add(pi)

def create_purchase_invoice_entries(pi:PurchaseInvoices, session:Session):
    cash_account = session.get(Accounts, 3210)
    bank_account = session.get(Accounts, 3211)
    vendor_account = pi.vendor.account
    discount_account = session.get(Accounts, 5140)
    
    cr_account = cash_account if pi.transaction_type == TransactionTypes.Cash else bank_account if pi.transaction_type == TransactionTypes.Bank else vendor_account
    
    rounded_off_account = session.get(Accounts, 5141)

    rounded_off_amount = pi.rounded_off

    if not rounded_off_amount <= 0:
        round_off_dr = create_dr_entry(account=cr_account, amount=rounded_off_amount, pi=pi)
        round_off_cr = create_cr_entry(account=rounded_off_account, amount=rounded_off_amount, pi=pi)
        
        round_off_dr.cr_entries.append(round_off_cr)
    

    for line_item in pi.line_items:
        item_account = line_item.item.inventory_account
        tax = line_item.item.gst_input if pi.state_type == StateType.Intra else line_item.item.igst_input

        if not tax:
            raise ValueError(f'Failed to determine correct tax account.')

        item_value = (line_item.price * line_item.quantity)
        discount_amount = line_item.discount_amount
        gst_amount = (item_value - line_item.discount_amount) * tax.rate / 100
        
        p_inv_dr_en = create_dr_entry(account=item_account,amount=item_value, pi=pi)
        gst_dr_en = create_dr_entry(account=tax.account, amount=gst_amount, pi=pi)

        p_inv_cr_en = create_cr_entry(account=cr_account, amount=item_value, pi=pi)
        gst_cr_en = create_cr_entry(account=cr_account, amount=gst_amount, pi=pi)
        
        if not discount_amount <= 0:
            p_dis_dr_en = create_dr_entry(account=cr_account, amount=discount_amount, pi=pi)
            p_dis_cr_en = create_cr_entry(account=discount_account, amount=discount_amount, pi=pi)
            p_dis_dr_en.cr_entries.append(p_dis_cr_en)

        p_inv_dr_en.cr_entries.append(p_inv_cr_en)
        gst_dr_en.cr_entries.append(gst_cr_en)
    
    session.add(pi)

def update_po(order:PurchaseOrders, session:Session):
    if order.status == OrderStatus.Fulfilled:
        raise ValueError("The Purchase Order Status is Fulfilled.")

    purchased_items = {}
    
    for i in order.purchase_invoices:
        for item in i.line_items:
            if not item.item.id in purchased_items.keys():
                purchased_items.update({item.item.id : item.quantity})
            else:
                purchased_items[item.item.id] += item.quantity
    
    for i in order.line_items:
        if i.quantity == purchased_items[i.item.id]:
            order.status = OrderStatus.Fulfilled
        else:
            order.status = OrderStatus.Pending

    session.add(order)            



def create_purchase_return_voucher(prv:PurchaseReturnVoucherBase, pi:PurchaseInvoices, session:Session):

    pi_vendor = pi.vendor    
    vendor = session.get(Vendors, prv.vendor_id)

    if pi_vendor and vendor:
        if pi_vendor != vendor:
            raise ValueError("Invoice Vendor and Return Vendor can not be diffrent.")

    new_return_voucher = PurchaseReturnVouchers.from_orm(prv, update={
        'purchase_invoice' : pi, 'vendor' : vendor
    })

    return new_return_voucher

def create_purchase_return_line_items(prv:PurchaseReturnVouchers, line_items:List[PRLineItemsBase], session:Session):
    for line_item in line_items:
        
        pi_line_item = session.get(PILineItems, line_item.pi_line_item_id)

        inventory = session.get(InventoryItems, line_item.pi_line_item_id)
        
        if not pi_line_item:
            raise ValueError(f"Item {inventory.name} is not a Purchase Invoice Line Item")
        
        stock = pi_line_item.stock

        if stock.quantity < line_item.quantity:
            raise ValueError(f"Return quantity of {line_item.quantity} is more than the available stock for item {inventory.name} of {stock.quantity}")
        
        pi_line_item.stock.quantity -= line_item.quantity


        new_line_item = PRLineItems(
            item_id=inventory.id,
            pi_line_item_id=line_item.pi_line_item_id,
            pi_line_item=pi_line_item,
            quantity=line_item.quantity,
            item=inventory,
            pr_id=prv.id,
            pr=prv,
            stock_id=stock.id,
            stock=stock
        )

        session.add(new_line_item)
    
    return True

def create_purchase_return_entries(pi:PurchaseInvoices, pr:PurchaseReturnVouchers, session:Session):
    
    vendor = pi.vendor
    discount_account = session.get(Accounts, 5140)

    for line_item in pr.line_items:
        pi_line_item = session.get(PILineItems, line_item.pi_line_item_id)
    
        item_value = pi_line_item.price * line_item.quantity
        

        tax_value = 0
        tax_account:Accounts = None
        
        discount_value = item_value * line_item.pi_line_item.discount_rate / 100

        if pi.state_type == StateType.Intra:
            tax_account = line_item.item.gst_input.account
            tax_value = (item_value - discount_value) * line_item.item.gst_input.rate / 100
        
        if pi.state_type == StateType.Inter:
            tax_account = line_item.item.igst_input.account
            tax_value = (item_value - discount_value) * line_item.item.igst_input.rate / 100


        purchase_dr_entry = create_dr_entry(
            amount= item_value - discount_value + tax_value,
            account=vendor.account,
            prv=pr,
            pi=pi
        )

        inventory_entry = create_cr_entry(
            amount=item_value,
            account=line_item.item.inventory_account,
            prv=pr,
            pi=pi
        )

        tax_entry = create_cr_entry(
            amount=tax_value,
            account = tax_account,
            prv=pr,
            pi=pi
        )

        if not discount_value == 0:
            discount_entry = create_dr_entry(
                amount=discount_value,
                account=discount_account,
                prv=pr,
                pi=pi
            )
            discount_entry.cr_entries.append(inventory_entry)

        purchase_dr_entry.cr_entries.append(tax_entry)
        purchase_dr_entry.cr_entries.append(inventory_entry)
    
    session.add(pi)
    session.add(pr)

def create_purchase_payment_journal(payment_voucher:JournalBase):
    new_payment_voucher = Journals(
        doc_date = payment_voucher.doc_date,
        doc_prefix = "Pay.V.-",
        doc_number =  payment_voucher.doc_number,
        doc_type = DocumentTypes.PaymentVoucher,
        narration = payment_voucher.narration,
        master_entry_type = EntryType.Credit
    )
    return new_payment_voucher

def create_payment_entries(payment_account_id:int, vendor_id:int, pi_id:int, journal:Journals, amount:float, session:Session):
    payment_account = session.get(Accounts, payment_account_id)
    vendor = session.get(Vendors, vendor_id)
    purchase_invoice = session.get(PurchaseInvoices, pi_id)

    if not payment_account:
        raise ValueError(f"Account for making payment with id {payment_account_id} does not exist.")
    
    if not vendor:
        raise  ValueError(f"Vendor id {vendor_id} does not exist.")

    if not purchase_invoice:
        raise ValueError(f"Purchase Invoice with id {pi_id} does not exist.")


    payment_cr_entry = create_cr_entry(account=payment_account, amount=amount, journal=journal, pi=purchase_invoice)
    payment_dr_entry = create_dr_entry(account=vendor.account, amount=amount, journal=journal, pi=purchase_invoice)

    payment_dr_entry.cr_entries.append(payment_cr_entry)

    session.add(purchase_invoice)
    session.add(journal)
    session.add(vendor)
