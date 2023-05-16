from enum import Enum

class DocumentTypes(Enum):
    Journal:str = "Journal Voucher"
    CashVoucher:str = "Cash Voucher"
    BankVoucher:str = "Bank Voucher"
    DebitNote:str = "Debit Note"
    CreditNote:str = "Credit Note"
    ContraVoucher:str = "Contra Voucher"
    ReceiptVoucher:str = "Receipt Voucher"
    PaymentVoucher:str = "Payment Voucher"
    DepricationVoucher:str = "Depriciation Voucher"
    SalesOrder:str = "Sales Order"
    PurchaseOrder:str = "Purchase Order"
    SalesInvoice:str = "Sales Invoice"
    SalesReturnVoucher:str = "Sales Return Voucher"
    PurchaseInvoice:str = "Purchase Invoice"
    PurchaseReturnVoucher:str = "Purchase Return Voucher"
    TaxVoucher:str = "Tax Voucher"

class TransactionTypes(Enum):
    Cash:int = 1
    Bank:int = 2
    Credit:int = 3

class StateType(Enum):
    Intra:int = 1
    Inter:int = 2

class OrderStatus(Enum):
    Fulfilled:int = 1
    Pending:int = 0
    Cancelled:int = -1

class CashFlowStatus(Enum):
    NonCashAdj:str = "Non Cash Adjustment"
    CurrentAssets:str = "Current Assets"
    CurrentLiabilities:str = "Current Liabilities"
    InterestIncome:str = "Interest Income"
    DividentReceived:str = "Divident Received"
    FixedAssets:str = "Fixed Assets"
    Investments:str = "Investments"
    Equity:str = "Equity"
    TermLoans:str = "Term Loans"
    Debentures:str = "Debentures"
    InterestPaid:str = "Interest Paid"
    DividentPaid:str = "Divident Paid"