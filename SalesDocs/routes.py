from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from field_types import StateType
from Inventory.models import LineItemBase, SRLineItemsBase
from Journals.models import JournalBase
from .models import SalesOrderBase, SalesOrders, SalesInvoiceBase, SalesInvoices, SalesReturnVoucherBase, SalesReturnVouchers, ReceiptRequest
from .crud import (
    create_sales_order, 
    create_sales_order_line_items, 
    create_sales_invoice, 
    create_sales_invoice_line_items, 
    create_sales_entries,
    update_so,
    create_sales_return_voucher,
    create_sr_line_items,
    create_sales_return_entries,
    create_receipt_entries,
    create_sales_receipt_journal
)

sale_router = APIRouter(prefix="/sales", tags=["Sales"])

@sale_router.get("/orders")
def read_all_sales_orders(session:Session=Depends(get_session)):
    orders = session.exec(select(SalesOrders)).all()
    return [
        {
            "order" : order,
            "customer" : order.customer,
            'value' : sum([item.price * item.quantity for item in order.line_items]),
            'discount' : sum([item.discount_amount for item in order.line_items]),
            'tax' : sum([((item.price * item.quantity)-item.discount_amount) * item.item.gst_input.rate / 100 for item in order.line_items]),
            'terms' : order.terms.terms,
            'items' :  [
                    {   
                        "id" : item.item.id,
                        "name" : item.item.name,
                        "unit_name" : item.item.unit.name,
                        "unit_id" : item.item.unit_id,
                        "line_item_id" : item.id,
                        "price" : item.price,
                        "quantity" : item.quantity,
                        "discount_rate" : item.discount_rate,
                        "discount_amount" : item.discount_amount,
                        "tax_name" : item.item.gst_output.name if order.state_type == StateType.Intra else item.item.igst_output.name,
                        "tax_id" : item.item.gst_output.id if order.state_type == StateType.Inter else item.item.igst_output.id,
                        "tax_amount" : ((item.price * item.quantity) - item.discount_amount) * item.item.gst_input.rate / 100,
                        "tax_rate" : item.item.gst_output.rate
                    } for item in order.line_items
                ],
            'sales_invoice_id' : [invoice.id for invoice in order.invoices]
        } for order in orders
    ]

@sale_router.get("/order/{id}")
def read_sales_order_by_id(id:int, session:Session=Depends(get_session)):
    order = session.get(SalesOrders, id)
    
    if not order:
        raise HTTPException(
            status_code = 404, detail = f"Sales Order with id {id} does not exist."
        )
    
    return {
            "order" : order,
            "customer" : order.customer,
            'value' : sum([item.price * item.quantity for item in order.line_items]),
            'discount' : sum([item.discount_amount for item in order.line_items]),
            'tax' : sum([((item.price * item.quantity)-item.discount_amount) * item.item.gst_input.rate / 100 for item in order.line_items]),
            'terms' : order.terms.terms,
            'items' :  [
                    {   
                        "id" : item.item.id,
                        "name" : item.item.name,
                        "unit_name" : item.item.unit.name,
                        "unit_id" : item.item.unit_id,
                        "line_item_id" : item.id,
                        "price" : item.price,
                        "quantity" : item.quantity,
                        "discount_rate" : item.discount_rate,
                        "discount_amount" : item.discount_amount,
                        "tax_name" : item.item.gst_output.name if order.state_type == StateType.Intra else item.item.igst_output.name,
                        "tax_id" : item.item.gst_output.id if order.state_type == StateType.Inter else item.item.igst_output.id,
                        "tax_amount" : ((item.price * item.quantity) - item.discount_amount) * item.item.gst_input.rate / 100,
                        "tax_rate" : item.item.gst_output.rate
                    } for item in order.line_items
                ],
            'sales_invoice_id' : [inv.id for inv in order.invoices]
        }

@sale_router.get("/invoices")
def read_all_sales_invoices(session:Session=Depends(get_session)):
    invoices = session.exec(select(SalesInvoices)).all()
    
    if not invoices:
        return []

    return [
        {
            'invoice' : invoice,
            'order_number' : invoice.sales_order,
            'customer' : invoice.customer,
            'value' : sum([item.price * item.quantity for item in invoice.line_items]),
            'discount' : sum([item.discount_amount for item in invoice.line_items]),
            'tax' : sum([((item.price * item.quantity)-item.discount_amount) * item.item.gst_input.rate / 100 for item in invoice.line_items]),
            "receipt_amount" : sum([entry.amount for entry in invoice.dr_entries if entry.journal]),
            'terms' : invoice.terms.terms,
            'items' :  [
                    {   
                        "id" : item.item.id,
                        "name" : item.item.name,
                        "unit_name" : item.item.unit.name,
                        "unit_id" : item.item.unit_id,
                        "line_item_id" : item.id,
                        "price" : item.price,
                        "quantity" : item.quantity,
                        "discount_rate" : item.discount_rate,
                        "discount_amount" : item.discount_amount,
                        "tax_name" : item.item.gst_output.name if invoice.state_type == StateType.Intra else item.item.igst_output.name,
                        "tax_id" : item.item.gst_output.id if invoice.state_type == StateType.Inter else item.item.igst_output.id,
                        "tax_amount" : ((item.price * item.quantity) - item.discount_amount) * item.item.gst_input.rate / 100,
                        "tax_rate" : item.item.gst_output.rate
                    } for item in invoice.line_items
                ],
            "dr_entries" : invoice.dr_entries,
            "cr_entries" : invoice.cr_entries
        } for invoice in invoices
    ]

@sale_router.get("/invoice/{id}")
def read_sales_invoice_by_id(id:int, session:Session=Depends(get_session)):
    invoice = session.get(SalesInvoices, id)
    if not invoice:
        raise HTTPException(
            status_code=404, detail=f"Sales Invoice with id {id} does not exist."
        )
    return {
            'invoice' : invoice,
            'order_number' : invoice.sales_order,
            'customer' : invoice.customer,
            'value' : sum([item.price * item.quantity for item in invoice.line_items]),
            'discount' : sum([item.discount_amount for item in invoice.line_items]),
            'tax' : sum([((item.price * item.quantity)-item.discount_amount) * item.item.gst_input.rate / 100 for item in invoice.line_items]),
            "receipt_amount" : sum([entry.amount for entry in invoice.dr_entries if entry.journal]),
            'terms' : invoice.terms.terms,
            'items' :  [
                    {   
                        "id" : item.item.id,
                        "name" : item.item.name,
                        "unit_name" : item.item.unit.name,
                        "unit_id" : item.item.unit_id,
                        "line_item_id" : item.id,
                        "price" : item.price,
                        "quantity" : item.quantity,
                        "discount_rate" : item.discount_rate,
                        "discount_amount" : item.discount_amount,
                        "tax_name" : item.item.gst_output.name if invoice.state_type == StateType.Intra else item.item.igst_output.name,
                        "tax_id" : item.item.gst_output.id if invoice.state_type == StateType.Inter else item.item.igst_output.id,
                        "tax_amount" : ((item.price * item.quantity) - item.discount_amount) * item.item.gst_input.rate / 100,
                        "tax_rate" : item.item.gst_output.rate
                    } for item in invoice.line_items
                ],
            "dr_entries" : invoice.dr_entries,
            "cr_entries" : invoice.cr_entries
        }

@sale_router.post("/order")
def add_sales_order(order:SalesOrderBase, line_items:List[LineItemBase], session:Session=Depends(get_session)):
    try:
        new_order = create_sales_order(order=order, session=session)
        session.add(new_order)
        print(new_order)
        create_sales_order_line_items(so=new_order, line_items=line_items, session=session)
        session.commit()
        session.refresh(new_order)
        return {
        "order" : new_order,
        "items" : [
                {   "id" : item.item.id,
                    "name" : item.item.name,
                    "unit" : item.item.unit.name,
                    "unit_id" : item.item.unit_id,
                    "tax_name" : item.item.gst_output.name if new_order.state_type == StateType.Intra else item.item.igst_output.name,
                    "tax_id" : item.item.gst_output.id if new_order.state_type == StateType.Inter else item.item.igst_output.id,
                    "quantity" : item.quantity,
                    "price" : item.price,
                    "discount_rate" : item.discount_rate,
                    "discount_amount" : item.discount_amount
                } for item in new_order.line_items
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

@sale_router.post("/invoice")
def add_sales_invoice(invoice:SalesInvoiceBase, line_items:List[LineItemBase], session:Session=Depends(get_session)):
    print(invoice)
    try:
        new_invoice = create_sales_invoice(invoice=invoice, session=session)
        session.add(new_invoice)

        create_sales_invoice_line_items(si=new_invoice, line_items=line_items, session=session)
        create_sales_entries(si=new_invoice, session=session)
        print("created entries")
        if new_invoice.so_id:
            update_so(order=session.get(SalesOrders, new_invoice.so_id), session=session)


        session.commit()
        session.refresh(new_invoice)
        return {
            "invoice" : new_invoice,
            "items" :    [
                {   "id" : item.item.id,
                    "name" : item.item.name,
                    "unit" : item.item.unit.name,
                    "unit_id" : item.item.unit_id,
                    "tax_name" : item.item.gst_output.name if new_invoice.state_type == StateType.Intra else item.item.igst_output.name,
                    "tax_id" : item.item.gst_output.id if new_invoice.state_type == StateType.Inter else item.item.igst_output.id,
                    "quantity" : item.quantity,
                    "price" : item.price,
                    "discount_rate" : item.discount_rate,
                    "discount_amount" : item.discount_amount
                } for item in new_invoice.line_items
            ],
            "dr_entries" : new_invoice.dr_entries,
            "cr_entries" : new_invoice.cr_entries
        }
    except Exception as e:
        raise HTTPException(
            status_code=403, detail=str(e)
        )

@sale_router.patch("/return")
def add_sales_return_voucher(voucher:SalesReturnVoucherBase, line_items:List[SRLineItemsBase], session:Session=Depends(get_session)):
    si = session.get(SalesInvoices, voucher.si_id)

    if not si:
        raise HTTPException(
            status_code=404, detail=f"Sales invoice with id {voucher.si_id} does not exist."
        )
    
    try:
        new_voucher = create_sales_return_voucher(voucher=voucher, session=session)
        session.add(new_voucher)
        create_sr_line_items(line_items=line_items, si=si, sr=new_voucher, session=session)
        create_sales_return_entries(si=si, sr=new_voucher, session=session)
        session.commit()
        session.refresh(new_voucher)
        return {
            'voucher' : new_voucher,
            'items' : new_voucher.line_items,
            'dr_entries' : new_voucher.dr_entries,
            'cr_entries' : new_voucher.cr_entries
        }
    except Exception as e:
        raise HTTPException(
            status_code=403, detail=str(e)
        )

@sale_router.post("/receipt")
def receive_dales_payment(receipt_voucher:JournalBase, receipt_request:ReceiptRequest, session:Session=Depends(get_session)):
    try:
        new_receipt_journal = create_sales_receipt_journal(receipt_voucher=receipt_voucher)
        session.add(new_receipt_journal)
        create_receipt_entries(
            receipt_account_id=receipt_request.receipt_account_id,
            customer_id=receipt_request.customer_id, 
            si_id=receipt_request.si_id, 
            journal=new_receipt_journal, 
            amount=receipt_request.amount, 
            session=session
            )
        session.commit()
        session.refresh(new_receipt_journal)
        return {
            'journal' : new_receipt_journal,
            'dr_entries' : new_receipt_journal.dr_entries,
            'cr_entries' : new_receipt_journal.cr_entries
        }
    except Exception as e:
        raise HTTPException(
            status_code=403, detail=str(e)
        )
    