from typing import defaultdict, Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from field_types import StateType
from Inventory.models import LineItemBase, PILineItems, POLineItems, PRLineItems, PRLineItemsBase
from Journals.models import JournalBase 
from .models import (
    PurchaseInvoicesBase, 
    PurchaseInvoices, 
    PurchaseOrderBase, 
    PurchaseOrders, 
    PurchaseReturnVoucherBase, 
    PurchaseReturnVouchers, 
    PayementRequest
)
from .crud import (
    create_purhcase_order, 
    create_po_line_items,
    create_purchase_invoice,
    create_purchase_invoice_line_items,
    create_purchase_invoice_entries,
    update_po,
    create_purchase_return_voucher,
    create_purchase_return_line_items,
    create_purchase_return_entries,
    create_purchase_payment_journal,
    create_payment_entries
)

purchase_router = APIRouter(prefix='/purchase', tags=["Purchase"])

@purchase_router.get("/invoices")
def read_all_purchase_invoices(session:Session = Depends(get_session)):
    invoices = session.exec(select(PurchaseInvoices)).all()
    return [
        {
            'invoice' : invoice,
            'order_number' : invoice.purchase_order.doc_number if invoice.purchase_order else None,
            'vendor' : invoice.vendor,
            'dr_entries' : invoice.dr_entries,
            'cr_entries' : invoice.cr_entries,
            'value' : sum([item.price * item.quantity for item in invoice.line_items]),
            'discount' : sum([item.discount_amount for item in invoice.line_items]),
            'tax' : sum([((item.price * item.quantity)-item.discount_amount) * item.item.gst_input.rate / 100 for item in invoice.line_items]),
            "payment_amount" : sum([entry.amount for entry in invoice.dr_entries if entry.journal]),
            'terms' : invoice.terms.terms,
            'items' : [{
                "name" : item.item.name,
                "unit_name" : item.item.unit.name,
                "id" : item.item.id,
                "line_item_id" : item.id,
                "price" : item.price,
                "quantity" : item.quantity,
                "discount_rate" : item.discount_rate,
                "discount_amount" : item.discount_amount,
                "tax_name" : item.item.gst_input.name if invoice.state_type == StateType.Intra else item.item.igst_input.name,
                "tax_id" : item.item.gst_input.id if invoice.state_type == StateType.Inter else item.item.igst_input.id,
                "tax_amount" : ((item.price * item.quantity) - item.discount_amount) * item.item.gst_input.rate / 100,
                "tax_rate" : item.item.gst_input.rate,
            } for item in invoice.line_items],
            'return_vouchers_id' : [voucher.id for voucher in invoice.return_vouchers] 
        } for invoice in invoices
    ]

@purchase_router.get("/invoice/{id}")
def read_purchase_invoice_by_id(id:int, session:Session=Depends(get_session)):
    invoice = session.get(PurchaseInvoices, id)
    if not invoice:
        raise HTTPException(
            status_code=404, detail=f"Purchase Invoice with id {id} does not exist."
        )
    return {
        'invoice' : invoice,
        'vendor' : invoice.vendor,
        'dr_entries' : invoice.dr_entries,
        'cr_entries' : invoice.cr_entries,
        'value' : sum([item.price * item.quantity for item in invoice.line_items]),
        'discount' : sum([item.discount_amount for item in invoice.line_items]),
        'tax' : sum([((item.price * item.quantity)-item.discount_amount) * item.item.gst_input.rate / 100 for item in invoice.line_items]),
        "payment_amount" : sum([entry.amount for entry in invoice.dr_entries if entry.journal]),
        'terms' : invoice.terms.terms,
        'items' : [{
            "name" : item.item.name,
            "unit_name" : item.item.unit.name,
            "id" : item.item.id,
            "line_item_id" : item.id,
            "price" : item.price,
            "quantity" : item.quantity,
            "discount_rate" : item.discount_rate,
            "discount_amount" : item.discount_amount,
            "tax_name" : item.item.gst_input.name if invoice.state_type == StateType.Intra else item.item.igst_input.name,
            "tax_id" : item.item.gst_input.id if invoice.state_type == StateType.Inter else item.item.igst_input.id,
            "tax_amount" : ((item.price * item.quantity) - item.discount_amount) * item.item.gst_input.rate / 100,
            "tax_rate" : item.item.gst_input.rate
        } for item in invoice.line_items],
        'return_vouchers_id' : [voucher.id for voucher in invoice.return_vouchers] 
    }

@purchase_router.get("/orders")
def read_all_purchase_orders(session:Session=Depends(get_session)):
    purchase_orders = session.exec(select(PurchaseOrders)).all()
    return [
        {
            'order' : order,
            'vendor' : order.vendor,
            'value' : sum([item.price * item.quantity for item in order.line_items]),
            'discount' : sum([item.discount_amount for item in order.line_items]),
            'tax' : sum([((item.price * item.quantity)-item.discount_amount) * item.item.gst_input.rate / 100 for item in order.line_items]),
            'terms' : order.terms.terms,
            'items' : [{
                "name" : item.item.name,
                "unit_name" : item.item.unit.name,
                "id" : item.item.id,
                "line_item_id" : item.id,
                "price" : item.price,
                "quantity" : item.quantity,
                "discount_rate" : item.discount_rate,
                "discount_amount" : item.discount_amount,
                "tax_name" : item.item.gst_input.name if order.state_type == StateType.Intra else item.item.igst_input.name,
                "tax_id" : item.item.gst_input.id if order.state_type == StateType.Inter else item.item.igst_input.id,
                "tax_amount" : ((item.price * item.quantity) - item.discount_amount) * item.item.gst_input.rate / 100,
                "tax_rate" : item.item.gst_input.rate
            } for item in order.line_items],
            'purchase_invoice_id' : [invoice.id for invoice in order.purchase_invoices]
        } for order in purchase_orders
    ]

@purchase_router.get("/order/{id}")
def read_purchase_order_by_id(id:int, session:Session=Depends(get_session)):
    order = session.get(PurchaseOrders, id)
    if not order:
        raise HTTPException(
            status_code=404, detail=f"Purchase Order with id {id} does not exist."
        )
    return {
            'order' : order,
            'vendor' : order.vendor,
            'value' : sum([item.price * item.quantity for item in order.line_items]),
            'discount' : sum([item.discount_amount for item in order.line_items]),
            'tax' : sum([((item.price * item.quantity)-item.discount_amount) * item.item.gst_input.rate / 100 for item in order.line_items]),
            'terms' : order.terms.terms,
            'items' : [{
                "name" : item.item.name,
                "unit_name" : item.item.unit.name,
                "id" : item.item.id,
                "line_item_id" : item.id,
                "price" : item.price,
                "quantity" : item.quantity,
                "discount_rate" : item.discount_rate,
                "discount_amount" : item.discount_amount,
                "tax_name" : item.item.gst_input.name if order.state_type == StateType.Intra else item.item.igst_input.name,
                "tax_id" : item.item.gst_input.id if order.state_type == StateType.Inter else item.item.igst_input.id,
                "tax_amount" : ((item.price * item.quantity) - item.discount_amount) * item.item.gst_input.rate / 100,
                "tax_rate" : item.item.gst_input.rate
            } for item in order.line_items],
            'purchase_invoice_id' : [invoice.id for invoice in order.purchase_invoices]
        }

@purchase_router.post("/order")
def add_purchase_order(po:PurchaseOrderBase, line_items:List[LineItemBase], session:Session=Depends(get_session)):
    new_po = create_purhcase_order(order=po, session=session)
    session.add(new_po)
    create_po_line_items(items=line_items,  po=new_po, session=session)
    session.commit()
    session.refresh(new_po)
    return {
            'order' : new_po,
            'items' : [{
                "name" : item.item.name,
                "id" : item.item.id,
                "line_item_id" : item.id,
                "price" : item.price,
                "quantity" : item.quantity,
                "discount_rate" : item.discount_rate,
                "discount_amount" : item.discount_amount,
                "tax_name" : item.item.gst_input.name if new_po.state_type == StateType.Intra else item.item.igst_input.name,
                "tax_id" : item.item.gst_input.id if new_po.state_type == StateType.Inter else item.item.igst_input.id,
            } for item in new_po.line_items],
            'purchase_invoice_id' : [invoice.id for invoice in new_po.purchase_invoices]
        }

@purchase_router.post("/invoice")
def add_purchase_invoice(invoice:PurchaseInvoicesBase, line_items:List[LineItemBase], session:Session=Depends(get_session)):
    try:
        new_invoice = create_purchase_invoice(invoice=invoice, session=session)
        session.add(new_invoice)
        
        create_purchase_invoice_line_items(items=line_items, pi=new_invoice, session=session)
        create_purchase_invoice_entries(pi=new_invoice, session=session)
        
        if new_invoice.po_id:
            update_po(order=session.get(PurchaseOrders, new_invoice.po_id), session=session)
        
        session.commit()
        session.refresh(new_invoice)
        
        return {
            'invoice' : new_invoice,
            'dr_entries' : new_invoice.dr_entries,
            'cr_entries' : new_invoice.cr_entries,
            'items' : [{
                "name" : item.item.name,
                "id" : item.item.id,
                "line_item_id" : item.id,
                "price" : item.price,
                "quantity" : item.quantity,
                "discount_rate" : item.discount_rate,
                "discount_amount" : item.discount_amount,
                "tax_name" : item.item.gst_input.name if new_invoice.state_type == StateType.Intra else item.item.igst_input.name,
                "tax_id" : item.item.gst_input.id if new_invoice.state_type == StateType.Inter else item.item.igst_input.id,
        } for item in new_invoice.line_items],
        'return_vouchers_id' : [voucher.id for voucher in new_invoice.return_vouchers] 
        }
    except Exception as e:
        raise HTTPException(
            status_code=403, detail=str(e)
        )

@purchase_router.patch("/invoice")
def add_purchase_return_voucher(
    voucher:PurchaseReturnVoucherBase, 
    line_items:List[PRLineItemsBase],
    session:Session=Depends(get_session)
    ):
        pi = session.get(PurchaseInvoices, voucher.pi_id)

        if not pi:
            raise HTTPException(
                status_code=404, detail=f"Purchase Invoice with id {id} does not exist."
            )
        
        try:
            new_voucher = create_purchase_return_voucher(prv=voucher, pi=pi, session=session)
            session.add(new_voucher)
            create_purchase_return_line_items(prv=new_voucher, line_items=line_items, session=session)
            create_purchase_return_entries(pi=pi, pr=new_voucher, session=session)
       
        except Exception as e:
            if not isinstance(e, HTTPException):
                raise HTTPException(
                    status_code=403, detail=str(e)
                )

        session.commit()
        session.refresh(new_voucher)

        return {
            'voucher' : new_voucher,
            'items' : [
                {
                    "name" : item.item.name,
                    "id" : item.item.id,
                    "line_item_id" : item.id,
                    "price" : item.pi_line_item.price,
                    "quantity" : item.quantity,
                    "discount_rate" : item.pi_line_item.discount_rate,
                    "discount_amount" : (item.pi_line_item.price * item.quantity) * item.pi_line_item.discount_rate / 100,
                    "tax_name" : item.item.gst_input.name if new_voucher.state_type == StateType.Intra else item.item.igst_input.name,
                    "tax_id" : item.item.gst_input.id if new_voucher.state_type == StateType.Inter else item.item.igst_input.id,
                } for item in new_voucher.line_items],
        }

@purchase_router.post("/payment")
def make_purchase_payment(payment_voucher:JournalBase, payment_request:PayementRequest, session:Session=Depends(get_session)):
    try:
        new_payment_journal = create_purchase_payment_journal(payment_voucher=payment_voucher)
        session.add(new_payment_journal)
        create_payment_entries(
            journal=new_payment_journal,
            payment_account_id=payment_request.payment_account_id,
            vendor_id=payment_request.vendor_id, 
            pi_id=payment_request.pi_id, 
            amount=payment_request.amount, session=session)
        session.commit()
        session.refresh(new_payment_journal)
        return {
            "journal" : new_payment_journal,
            "dr_entries" : new_payment_journal.dr_entries,
            "cr_entries" : new_payment_journal.cr_entries
        }
    except Exception as e:
        raise HTTPException(
            status_code=403, detail=str(e)
        )