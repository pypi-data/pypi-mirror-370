class BasePaymentError(Exception):
    """Base Payment Error"""


class PaymentError(BasePaymentError):
    """Payment Error"""


class PaymentImproperlyConfiguredError(PaymentError):
    """Payment Improperly Configured Error"""


class PaymentBackendDoesNotExistError(PaymentError):
    """PaymentBackend Does Not Exist Error"""
