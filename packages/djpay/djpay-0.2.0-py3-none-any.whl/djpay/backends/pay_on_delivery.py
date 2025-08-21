# standard
from typing import Any

# internal
from ..models import Bill
from .base import BaseBackend


class PayOnDelivery(BaseBackend):
    """Pay On Delivery"""

    identifier = "pay-on-delivery"
    label = "Pay on delivery"

    def pay(self, amount: int, **extra: Any) -> Bill:
        return Bill.objects.create(backend=self.identifier, amount=amount, extra=extra)

    def verify(self, bill: Bill, **kwargs: Any) -> Bill:
        # check for backend
        if bill.backend != self.identifier:
            self.error("Invalid bill.")
        # check verified status
        if bill.verified:
            self.error("Invalid bill.")
        # verify and return bill
        bill.verified = True
        bill.save(update_fields=["verified"])
        return bill
