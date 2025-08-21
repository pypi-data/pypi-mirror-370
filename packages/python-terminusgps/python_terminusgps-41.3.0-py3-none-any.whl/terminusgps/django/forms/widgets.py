from authorizenet import apicontractsv1
from django import forms


class CaptchaWidget(forms.widgets.CheckboxInput):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        print(f"{context = }")
        return context

    def check_test(self, value):
        return bool(value)


class CreditCardWidget(forms.widgets.MultiWidget):
    def __init__(self, widgets=(), attrs: dict | None = None) -> None:
        if not widgets:
            widgets = [
                forms.TextInput(attrs=attrs),
                forms.TextInput(attrs=attrs),
                forms.TextInput(attrs=attrs),
                forms.TextInput(attrs=attrs),
            ]
        super().__init__(widgets=widgets, attrs=attrs)

    def decompress(
        self, value: apicontractsv1.creditCardType | None
    ) -> list[str | None]:
        """Decompresses a :py:attr:`~authorizenet.apicontractsv1.creditCardType` into a list of strings."""
        if value is None:
            return [None, None, None, None]

        expiry_parts = value.expirationDate.split("-")
        return [value.cardNumber, expiry_parts[0], expiry_parts[1], value.cardCode]


class AddressWidget(forms.widgets.MultiWidget):
    def __init__(self, widgets=(), attrs: dict | None = None) -> None:
        if not widgets:
            widgets = [
                forms.TextInput(attrs=attrs),
                forms.TextInput(attrs=attrs),
                forms.TextInput(attrs=attrs),
                forms.TextInput(attrs=attrs),
                forms.TextInput(attrs=attrs),
            ]
        super().__init__(widgets=widgets, attrs=attrs)

    def decompress(
        self, value: apicontractsv1.customerAddressType | None
    ) -> list[str | None]:
        """Decompresses a :py:attr:`~authorizenet.apicontractsv1.customerAddressType` into a list of strings."""
        if value is None:
            return [None, None, None, None, None]

        return [value.address, value.city, value.state, value.country, value.zip]
