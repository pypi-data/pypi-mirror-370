import string

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.translation import gettext_lazy as _

from .session import WialonSession

if settings.configured and not hasattr(settings, "WIALON_TOKEN"):
    raise ImproperlyConfigured("'WIALON_TOKEN' setting is required.")


class WialonValidatorBase:
    def __init__(self) -> None:
        self.session = WialonSession()
        self.session.login(self.session.token)

    def __call__(self, value: str) -> None:
        raise NotImplementedError("Subclasses must implement this method.")


class WialonVinNumberValidator(WialonValidatorBase):
    def __call__(self, value: str) -> None:
        response = self.session.wialon_api.unit_get_vin_info(vin=value)
        if "error" in response["vin_lookup_result"].keys():
            raise ValidationError(
                _("Failed to get info for VIN # '%(value)s': '%(message)s'"),
                code="invalid",
                params={
                    "value": value,
                    "message": response["vin_lookup_result"].get("message", ""),
                },
            )


class WialonImeiNumberValidator(WialonValidatorBase):
    def __call__(self, value: str) -> None:
        response = self.session.wialon_api.core_search_items(
            **{
                "spec": {
                    "itemsType": "avl_unit",
                    "propName": "sys_id,sys_unique_id",
                    "propValueMask": f"*,*{value}*",
                    "sortType": "sys_id,sys_unique_id",
                },
                "force": 0,
                "flags": 1,
                "from": 0,
                "to": 0,
            }
        )
        if response is None or not response.get("items"):
            raise ValidationError(
                _("IMEI # '%(value)s' wasn't found in Wialon."),
                code="invalid",
                params={"value": value},
            )


def validate_imei_number(value: str) -> None:
    """Raises :py:exec:`ValidationError` if the value is an invalid IMEI number."""
    WialonImeiNumberValidator()(value)


def validate_vin_number(value: str) -> None:
    """Raises :py:exec:`ValidationError` if the value is an invalid VIN number."""
    if len(value) != 17:
        raise ValidationError(
            _("Whoops! VIN # must be exactly 17 characters in length, got %(length)s."),
            code="invalid",
            params={"length": len(value)},
        )
    WialonVinNumberValidator()(value)


def validate_wialon_password(value: str) -> None:
    """Raises :py:exec:`ValidationError` if the value represents an invalid Wialon password."""
    special_symbols_0: list[str] = ["!", "@", "#", "$", "%", "^", "*"]
    special_symbols_1: list[str] = ["(", ")", "[", "]", "-", "_", "+"]
    forbidden_symbols: list[str] = [",", ":", "&", "<", ">", "'"]

    if len(value) < 4:
        raise ValidationError(
            _("Password cannot be less than 4 characters in length, got %(len)s."),
            code="invalid",
            params={"len": len(value)},
        )
    if len(value) > 64:
        raise ValidationError(
            _("Password cannot be greater than 64 characters in length, got %(len)s."),
            code="invalid",
            params={"len": len(value)},
        )
    if not any([char for char in value if char in string.ascii_uppercase]):
        raise ValidationError(
            _("Password must contain at least one uppercase letter."), code="invalid"
        )
    if not any([char for char in value if char in string.ascii_lowercase]):
        raise ValidationError(
            _("Password must contain at least one lowercase letter."), code="invalid"
        )
    if not any(
        [char for char in value if char in special_symbols_0 + special_symbols_1]
    ):
        raise ValidationError(
            _("Password must contain at least one special symbol."), code="invalid"
        )
    for char in value:
        if char in forbidden_symbols:
            raise ValidationError(
                _("Password cannot contain forbidden character '%(char)s'."),
                code="invalid",
                params={"char": char},
            )
