# standard
from typing import List, Tuple

# dj
from django.utils.functional import cached_property

# internal
from .zibal import Zibal
from .base import BaseBackend
from .zarinpal import ZarinPal
from .pay_on_delivery import PayOnDelivery
from ..errors import PaymentBackendDoesNotExistError


class BackendsPool(object):
    """Backends Pool"""

    @cached_property
    def backends(self) -> List:
        return [ZarinPal, Zibal, PayOnDelivery]

    @cached_property
    def as_choices(self) -> List[Tuple[str, str]]:
        return [(backend.identifier, backend.label) for backend in self.backends]

    def get_class(self, identifier: str):
        for backend in self.backends:
            if identifier == backend.identifier:
                return backend
        raise PaymentBackendDoesNotExistError

    def get(self, identifier: str, config: dict | None = None) -> BaseBackend:
        backend_class = self.get_class(identifier)
        return backend_class(config)


backends_pool = BackendsPool()
