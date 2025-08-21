# standard
from typing import Any

# requests
import requests

# dj
from django.urls import reverse
from django.http import HttpRequest
from django.urls.exceptions import NoReverseMatch

# internal
from ..models import Bill
from .base import BaseBackend
from ..utils import absolute_reverse
from ..errors import PaymentImproperlyConfiguredError


SAMPLE_BILL_PK = 0
SUCCESS_STATUS_CODE = 100
PAY_ENDPOINT = "https://www.zarinpal.com/pg/StartPay/"
VERIFY_ENDPOINT = "https://api.zarinpal.com/pg/v4/payment/verify.json"
INITIAL_ENDPOINT = "https://api.zarinpal.com/pg/v4/payment/request.json"


class ZarinPal(BaseBackend):
    """ZarinPal"""

    identifier = "zarinpal"
    label = "ZarinPal"

    @classmethod
    def validate_config(cls, config: dict) -> dict:
        # extract required data
        currency = config.get("currency")
        merchant_id = config.get("merchant_id")
        callback_view_name = config.get("callback_view_name")

        # validate currency
        if (
            not currency
            or not isinstance(currency, str)
            or currency not in ["IRT", "IRR"]
        ):
            raise PaymentImproperlyConfiguredError("Invalid currency.")
        # validate merchant_id
        if not merchant_id or not isinstance(merchant_id, str):
            raise PaymentImproperlyConfiguredError("Invalid merchant_id.")
        # validate callback_view_name
        if not callback_view_name or not isinstance(callback_view_name, str):
            raise PaymentImproperlyConfiguredError("Invalid callback_view_name.")
        try:
            reverse(callback_view_name, kwargs={"bill_pk": SAMPLE_BILL_PK})
        except NoReverseMatch:
            raise PaymentImproperlyConfiguredError("Invalid callback_view_name.")

        return config

    @property
    def currency(self) -> str:
        return self._get_config("currency", "IRT")

    @property
    def merchant_id(self) -> str:
        return self._get_config("merchant_id")

    def get_callback_url(self, bill_pk: int, request: HttpRequest = None) -> str:
        callback_view_name = self._get_config("callback_view_name")
        callback_view_kwargs = {"bill_pk": bill_pk}
        # check for request:
        # if request is present, its means user needs to absolute url
        # otherwise there is no need to absolute and relative is also acceptable
        if request:
            return absolute_reverse(
                request, callback_view_name, kwargs=callback_view_kwargs
            )
        else:
            return reverse(callback_view_name, kwargs=callback_view_kwargs)

    def pay(self, amount: int, **extra: Any) -> Bill:
        # pop out request from extra
        request = extra.pop("request", None)
        # create bill
        bill = Bill.objects.create(
            backend=self.identifier,
            amount=amount,
            extra=extra,
        )
        # send initialize request
        data = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "currency": self.currency,
            "callback_url": self.get_callback_url(bill.pk, request),
            "description": "No description provided.",
        }
        res = requests.post(INITIAL_ENDPOINT, data=data).json()
        # extract data and errors from response
        res_data = res.get("data")
        res_errors = res.get("errors")
        # check for errors
        if res_errors:
            self.error(res_errors.get("message"))
        # check for invalid code
        if res_data.get("code") != SUCCESS_STATUS_CODE:
            self.error("Invalid code.")
        # there is no error and invalid-code so:
        # add redirect-url as next_step on bill instance
        # and return it as response
        bill.next_step = PAY_ENDPOINT + res_data["authority"]
        bill.save(update_fields=["next_step"])
        return bill

    def verify(self, bill: Bill, **kwargs: Any) -> Bill:
        # check for backend
        if bill.backend != self.identifier:
            self.error("Invalid bill.")
        # check verified status
        if bill.verified:
            self.error("Invalid bill.")
        # check for Authority in kwargs
        if "Authority" not in kwargs:
            self.error("Required Authority parameter not provided.")
        # send verify request
        data = {
            "authority": kwargs["Authority"],
            "amount": bill.amount,
            "merchant_id": self.merchant_id,
        }
        res = requests.post(VERIFY_ENDPOINT, data=data).json()
        # extract data and errors from response
        res_data = res.get("data")
        res_errors = res.get("errors")
        # check for errors
        if res_errors:
            self.error(res_errors.get("message"))
        # check for invalid code
        if res_data.get("code") != SUCCESS_STATUS_CODE:
            self.error("Invalid code.")
        # there is no error and invalid-code so:
        # 1) add ref_id as transaction_id on bill instance
        # 2) change verified status value to True
        # and return it as response
        bill.transaction_id = res_data["ref_id"]
        bill.verified = True
        bill.save(update_fields=["transaction_id", "verified"])
        return bill
