from typing import List
from sqlmodel import Session, select
from Accounts.models import Accounts
from Customers.models import Customers
from Inventory.models import InventoryItems, SILineItems, SOLineItems, SRLineItems, LineItemBase, SRLineItemsBase, ItemCategory
from Entries.models import EntryType
from Entries.crud import create_dr_entry, create_cr_entry
from Journals.models import JournalBase, Journals
from Terms.models import SalesOrderTerms, SalesInvoiceTerms
from field_types import TransactionTypes, StateType, OrderStatus
from .models import SalesInvoiceBase, SalesInvoices, SalesOrderBase, SalesOrders, SalesReturnVoucherBase, SalesReturnVouchers

def create_sales_order(order:SalesOrderBase, session:Session) -> SalesOrders:
    customer = session.get(Customers, order.customer_id)
    terms = session.get(SalesOrderTerms, order.terms_id)
    
    if not customer:
        raise ValueError(f"Customer with id {order.customer_id} does not exist.")
    
    new_sales_order = SalesOrders(
        doc_date=order.doc_date,
        doc_number=order.doc_number,
        state_type=order.state_type,
        terms_id=order.terms_id,
        terms=terms,
        customer_id=customer.id,
        customer=customer
    )
    return new_sales_order

def create_sales_order_line_items(so:SalesOrders, line_items:List[LineItemBase], session:Session) -> None:
    for line_item in line_items:
        inventory = session.get(InventoryItems, line_item.item_id)
        
        if not inventory:
            raise ValueError(f"Inventory Item with id {line_item.item_id} does not exist.")
        
        new_line_item = SOLineItems(
            item_id=inventory.id,
            item=inventory,
            price=line_item.price,
            quantity=line_item.quantity,
            discount_rate=line_item.discount_rate,
            discount_amount=(line_item.price * line_item.quantity) * line_item.discount_rate/100,
            so_id=so.id,
            so=so
        ) 

        session.add(new_line_item)

def create_sales_invoice(invoice:SalesInvoiceBase, session:Session) -> SalesInvoices:
    so = session.get(SalesOrders, invoice.so_id)
    so_customer = session.get(Customers, so.customer_id) if so else None
    customer = session.get(Customers, invoice.customer_id)
    terms = session.get(SalesInvoiceTerms, invoice.terms_id)

    if not customer:
        raise ValueError(f"Customer with id {invoice.customer_id} does not exist.")
    
    if so_customer and customer:
        if so_customer != customer:
            raise ValueError("Can not issue Sales Invoice to a diffrent cstomer than Sales Order Customer.")
    
    new_invoice = SalesInvoices(
        doc_date=invoice.doc_date,
        doc_number=invoice.doc_number,
        state_type=invoice.state_type,
        terms_id=terms.id if terms else None,
        terms=terms,
        customer_id=customer.id,
        customer=customer,
        so_id=so.id if so else None,
        so=so,
        transaction_type=invoice.transaction_type,
        rounded_off=invoice.rounded_off
    )
    return new_invoice

def handle_sale_stock(item:InventoryItems, line_item:SILineItems, session:Session):
    stocks = item.stocks
    sale_quantity = line_item.quantity
    available_quantity = sum([s.quantity for s in stocks]) 
    
    if available_quantity < sale_quantity:
        raise ValueError(f"Sale quantity of {sale_quantity} {item.unit.name} is greater than available stock for item {item.name} of {available_quantity} {item.unit.name}.")
    
    cogs = 0

    for stock in stocks:
        if sale_quantity > 0:
            if sale_quantity > stock.quantity:
                cogs += stock.quantity * stock.price
                sale_quantity -= stock.quantity
                stock.quantity = 0
                stock.sale_line_items.append(line_item)
                session.add(stock)
            if sale_quantity <= stock.quantity:
                cogs += sale_quantity * stock.price
                stock.quantity -= sale_quantity
                sale_quantity = 0
                stock.sale_line_items.append(line_item)
                session.add(stock)

    return cogs    

def create_sales_invoice_line_items(si:SalesInvoices, line_items:List[LineItemBase], session:Session):
    for line_item in line_items:
        inventory = session.get(InventoryItems, line_item.item_id)
        
        if not inventory:
            raise ValueError(f"Inventory Item with id {line_item.item_id} does not exist.")
        
        if si.sales_order:
            so_items = [l_item.item for l_item in si.sales_order.line_items]
            so_quantity = sum([l.quantity for l in si.sales_order.line_items if l.item_id == inventory.id])
        
            if inventory not in so_items:
                raise ValueError(f"Sale item {inventory.name} is not a sales order line item")
            
            if so_quantity < line_item.quantity:
                raise ValueError(f"Sale quantity for item {inventory.name} of {line_item.quantity} is more than order quantity of {so_quantity}")
            
        new_line_item = SILineItems(
            item_id=inventory.id,
            item=inventory,
            price=line_item.price,
            quantity=line_item.quantity,
            discount_rate=line_item.discount_rate,
            discount_amount=(line_item.price * line_item.quantity) * line_item.discount_rate/100,
            si_id=si.id,
            si=si
        )

        session.add(new_line_item)
        
        cogs = handle_sale_stock(item=inventory, line_item=new_line_item, session=session)

        new_line_item.cogs = cogs

        session.add(new_line_item)


def create_sales_entries(si:SalesInvoices, session:Session):
    customer_account = si.customer.account
    cash_account = session.get(Accounts, 3210)
    bank_account = session.get(Accounts, 3211)
    
    discount_account = session.get(Accounts, 4101)
    
    revenue_account_fin = session.get(Accounts, 5000)
    revenue_account_unfin = session.get(Accounts, 5001)
    revenue_account_raw = session.get(Accounts, 5002)

    raw_account = session.get(Accounts,4000)
    semi_account = session.get(Accounts, 4001)
    fin_account = session.get(Accounts, 4002)

    sale_dr_account = cash_account if si.transaction_type == TransactionTypes.Cash else bank_account if si.transaction_type == TransactionTypes.Bank else customer_account
    
    rounded_off_account = session.get(Accounts, 4102)

    rounded_off_amount = si.rounded_off

    if not rounded_off_amount <= 0:
        round_off_dr = create_dr_entry(account=rounded_off_account, amount=rounded_off_amount, si=si)
        round_off_cr = create_cr_entry(account=sale_dr_account, amount=rounded_off_amount, si=si)

        round_off_dr.cr_entries.append(round_off_cr)

    for line_item in si.line_items:
        item = line_item.item
        tax = line_item.item.gst_output if si.state_type == StateType.Intra else line_item.item.igst_output
        revenue_account = revenue_account_raw if item.item_category == ItemCategory.Raw else revenue_account_unfin if item.item_category == ItemCategory.Unfinished else revenue_account_fin
        cost_account = raw_account if item.item_category == ItemCategory.Raw else semi_account if item.item_category == ItemCategory.Unfinished else fin_account

        item_amount = line_item.price * line_item.quantity
        discount_amount = line_item.discount_amount
        gst_amount = (item_amount - discount_amount) * tax.rate / 100
             
        sale_dr_entry = create_dr_entry(account=sale_dr_account, amount=item_amount, si=si)
        sale_cr_enrty = create_cr_entry(account=revenue_account, amount=item_amount, si=si)

        sale_dr_entry.cr_entries.append(sale_cr_enrty)

        cost_dr_entry = create_dr_entry(account=cost_account, amount=line_item.cogs, si=si)
        cost_cr_entry = create_cr_entry(account=item.inventory_account, amount=line_item.cogs, si=si)

        cost_dr_entry.cr_entries.append(cost_cr_entry)

        gst_dr_entry = create_dr_entry(account=sale_dr_account, amount=gst_amount, si=si)
        gst_cr_entry = create_cr_entry(account=tax.account, amount=gst_amount, si=si)

        gst_dr_entry.cr_entries.append(gst_cr_entry)

        if not discount_amount <= 0:
            discount_dr_entry = create_dr_entry(account=discount_account, amount=discount_amount, si=si)
            discount_cr_entry = create_cr_entry(account=sale_dr_account, amount=discount_amount, si=si)

            discount_dr_entry.cr_entries.append(discount_cr_entry)

    session.add(si)

def update_so(order:SalesOrders, session:Session):
    if order.status == OrderStatus.Fulfilled:
        raise ValueError("The Sales Order is Fulfilled.")
    
    sold_items = {}

    for inv in order.invoices:
        for item in inv.line_items:
            if not item.item.id in sold_items.keys():
                sold_items.update({item.item.id : item.quantity})
            else:
                sold_items[item.item.id] += item.quantity
    
    for i in order.line_items:
        if i.quantity == sold_items[i.item.id]:
            order.status = OrderStatus.Fulfilled
        else:
            order.status = OrderStatus.Pending
    
    session.add(order)


def create_sales_return_voucher(voucher:SalesReturnVoucherBase, session:Session):
    sales_invoice = session.get(SalesInvoices, voucher.si_id)
    customer = sales_invoice.customer

    if not sales_invoice:
        raise ValueError(f"Sales Invoice with id {voucher.si_id} does not exist.")
    
    return_vocher = SalesReturnVouchers(
        doc_date=voucher.doc_date,
        doc_number=voucher.doc_number,
        customer_id=customer.id,
        customer=customer,
        si_id=sales_invoice.id,    
        sales_invoice=sales_invoice,
        state_type=voucher.state_type
    )

    return return_vocher

def create_sr_line_items(line_items:List[SRLineItemsBase], si:SalesInvoices, sr:SalesReturnVouchers, session:Session):

    for line_item in line_items:
    
        si_line_item = session.get(SILineItems, line_item.si_line_item_id)

        if not si_line_item:
            raise ValueError(f"Sales Return item not in sales invoice line items.")
        
        return_quantity = line_item.quantity
        sale_quantity = si_line_item.quantity

        if return_quantity > sale_quantity - sum([line_item.quantity for voucher in si.return_vouchers for line_item in voucher.line_items]):
            raise ValueError("Item return qantity can not be greater than sold quantity.")


        for stocks in si_line_item.stocks:
            if return_quantity > 0:
                line_item_quantity = stocks.line_item.quantity
                if return_quantity + stocks.quantity > line_item_quantity:
                    print("return + stock > than line item quantity")
                    print(return_quantity, line_item_quantity)
                    new_sr_line_item = SRLineItems(
                        si_line_item_id=si_line_item.id,
                        si_line_item=si_line_item,
                        quantity=line_item_quantity,
                        item_id=si_line_item.item.id,
                        item=si_line_item.item,
                        sr_id=sr.id,
                        sr=sr,
                        stock_id=stocks.id,
                        cogs=line_item_quantity * stocks.line_item.price
                    )
                    stocks.quantity = line_item_quantity
                    return_quantity -= line_item_quantity
                    stocks.sr_line_items.append(new_sr_line_item)
                
                if return_quantity + stocks.quantity <= line_item_quantity:
                    print("return + stock <= than line item quantity")
                    print(return_quantity, line_item_quantity)
                    new_sr_line_item = SRLineItems(
                        si_line_item_id=si_line_item.id,
                        si_line_item=si_line_item,
                        quantity=return_quantity,
                        item_id=si_line_item.item.id,
                        item=si_line_item.item,
                        sr_id=sr.id,
                        sr=sr,
                        stock_id=stocks.id,
                        cogs=return_quantity * stocks.line_item.price 
                    )
                    stocks.quantity += return_quantity
                    return_quantity = 0
                    stocks.sr_line_items.append(new_sr_line_item)
    
    session.add(new_sr_line_item)

def create_sales_return_entries(si:SalesInvoices, sr:SalesReturnVouchers, session:Session):
    customer = si.customer
    customer_account = customer.account
    discount_account = session.get(Accounts, 4101)
    revenue_account = session.get(Accounts, 5000)
    cogs_account = session.get(Accounts, 4002)
    

    for r_line_item in sr.line_items:
        
        si_line_item = r_line_item.si_line_item

        sale_value = (si_line_item.price * r_line_item.quantity)

        tax_value = 0
        tax_account = None

        discount_value = (sale_value * si_line_item.discount_rate / 100)

        if sr.state_type == StateType.Intra:
            tax_account = r_line_item.item.gst_output.account
            tax_value = (sale_value - discount_value) * r_line_item.item.gst_output.rate / 100

        if sr.state_type == StateType.Inter:
            tax_account = r_line_item.item.igst_output.account
            tax_value = (sale_value - discount_value) * r_line_item.item.igst_output.rate / 100
        
        sale_cr_entry = create_cr_entry(amount=sale_value-discount_value + tax_value, account=customer_account, srv=sr, si=si)

        sale_dr_entry = create_dr_entry(amount=sale_value - discount_value, account=revenue_account, srv=sr, si=si)

        sale_dr_entry.cr_entries.append(sale_cr_entry)

        if not discount_value == 0:
            discount_dr_entry = create_dr_entry(amount=discount_value, account=revenue_account, srv=sr, si=si)
            discount_cr_entry = create_cr_entry(amount=discount_value, account=discount_account, srv=sr, si=si)
            discount_dr_entry.cr_entries.append(discount_cr_entry)
        
        tax_dr_entry = create_dr_entry(amount=tax_value, account=tax_account, srv=sr, si=si)

        sale_cr_entry.dr_entries.append(tax_dr_entry)

        inventory_dr_entry = create_dr_entry(amount=r_line_item.cogs, account=r_line_item.item.inventory_account, srv=sr, si=si)
        inventory_cr_entry = create_cr_entry(amount=r_line_item.cogs, account=cogs_account, srv=sr, si=si)

        inventory_cr_entry.dr_entries.append(inventory_dr_entry)

    session.add(sr)

def create_sales_receipt_journal(receipt_voucher:JournalBase):
    new_receipt_voucher = Journals.from_orm(receipt_voucher, update={
        'master_entry_type' : EntryType.Debit, 'doc_prefix' : "Rec.V.-"
    })
    return new_receipt_voucher

def create_receipt_entries(receipt_account_id:int, customer_id:int, si_id:int, journal:Journals, amount:float, session:Session):
    receipt_account = session.get(Accounts, receipt_account_id)
    customer = session.get(Customers, customer_id)
    sales_invoice = session.get(SalesInvoices, si_id)

    if not receipt_account:
        raise ValueError(f"Account for receiveing payment with id {receipt_account_id} does not exist.")
    
    if not customer:
        raise ValueError(f"Customer with id {customer_id} does not exist.")
    
    if not sales_invoice:
        raise ValueError(f"Sales invoice with id {si_id} does not exist.")
    
    receipt_dr_entry = create_dr_entry(account=receipt_account, amount=amount, journal=journal, si=sales_invoice)
    receipt_cr_entry = create_cr_entry(account=customer.account, amount=amount,  journal=journal, si=sales_invoice)

    receipt_dr_entry.cr_entries.append(receipt_cr_entry)

    session.add(sales_invoice)
    session.add(journal)
    session.add(customer)
    