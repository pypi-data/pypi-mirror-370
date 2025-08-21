from collections.abc import Sequence

from authorizenet import apicontractsv1
from django import forms

from .widgets import AddressWidget, CreditCardWidget


class CreditCardField(forms.MultiValueField):
    require_all_fields = True

    def __init__(self, fields=(), widget=CreditCardWidget(), *args, **kwargs) -> None:
        if not fields:
            fields = (
                forms.CharField(label="Card #"),
                forms.IntegerField(label="Expiry Month", min_value=1, max_value=12),
                forms.IntegerField(label="Expiry Year"),
                forms.CharField(label="CCV #"),
            )
        super().__init__(fields=fields, widget=widget, *args, **kwargs)

    def compress(self, data_list: Sequence[str]) -> apicontractsv1.creditCardType:
        """Compresses ``data_list`` into a :py:obj:`~authorizenet.apicontractsv1.creditCardType`."""
        return apicontractsv1.creditCardType(
            **{
                "cardNumber": data_list[0],
                "expirationDate": f"{data_list[1]}-{data_list[2]}",
                "cardCode": data_list[3],
            }
        )


class AddressField(forms.MultiValueField):
    require_all_fields = True

    def __init__(self, fields=(), widget=AddressWidget(), *args, **kwargs) -> None:
        if not fields:
            fields = (
                forms.CharField(label="Street", max_length=128),
                forms.CharField(label="City", max_length=128),
                forms.CharField(label="State", max_length=64),
                forms.CharField(label="Zip #", min_length=5, max_length=10),
                forms.CharField(label="Country", max_length=2),
            )
        super().__init__(fields=fields, widget=widget, *args, **kwargs)

    def compress(self, data_list: Sequence[str]) -> apicontractsv1.customerAddressType:
        """Compresses ``data_list`` into a :py:obj:`~authorizenet.apicontractsv1.customerAddressType`."""
        return apicontractsv1.customerAddressType(
            **{
                "address": data_list[0],
                "city": data_list[1],
                "state": data_list[2],
                "zip": data_list[3],
                "country": data_list[4],
            }
        )
