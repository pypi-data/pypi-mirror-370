from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

VALID_COUNTRY_CODES = ("+1", "+52")


def validate_e164_phone_number(value: str) -> None:
    """Raises :py:exc:`~django.core.exceptions.ValidationError` if the value is not a valid `E.164 <https://en.wikipedia.org/wiki/E.164>`_ formatted phone number."""
    if not value:
        raise ValidationError(
            _("This field is required, got '%(value)s'"),
            code="invalid",
            params={"value": value},
        )
    if not value.startswith("+"):
        raise ValidationError(
            _("E.164 phone number must begin with a '+', got '%(char)s'."),
            code="invalid",
            params={"char": value[0]},
        )
    if " " in value:
        raise ValidationError(
            _("E.164 phone number cannot contain spaces, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )
    if "-" in value:
        raise ValidationError(
            _("E.164 phone number cannot contain hyphens, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )
    if len(value) < 12:
        raise ValidationError(
            _(
                "E.164 phone number cannot be less than 12 characters in length, got %(len)s."
            ),
            code="invalid",
            params={"len": len(value)},
        )
    if len(value) > 15:
        raise ValidationError(
            _(
                "E.164 phone number cannot be greater than 15 characters in length, got %(len)s."
            ),
            code="invalid",
            params={"len": len(value)},
        )

    country_code: str = value[:-10]
    area_code: str = value[-10:-7]
    subscriber_number: str = value[-7:]

    if len(country_code) < 2 or len(country_code) > 5:
        raise ValidationError(
            _(
                "E.164 phone number country code must be between 2 and 5 characters in length, got %(len)s."
            ),
            code="invalid",
            params={"len": len(country_code)},
        )
    if country_code not in VALID_COUNTRY_CODES:
        raise ValidationError(
            _(
                "E.164 phone number cannot contain an invalid country code, got '%(country_code)s'."
            ),
            code="invalid",
            params={"country_code": country_code},
        )
    if not len(area_code) == 3:
        raise ValidationError(
            _(
                "E.164 phone number must contain a 3-digit area code, got '%(area_code)s'."
            ),
            code="invalid",
            params={"area_code": area_code},
        )
    if not area_code.isdigit():
        raise ValidationError(
            _("E.164 phone number must have a valid area code, got '%(area_code)s'"),
            code="invalid",
            params={"area_code": area_code},
        )
    if not len(subscriber_number) == 7:
        raise ValidationError(
            _(
                "E.164 phone number must contain a 7-digit subscriber number, got '%(subscriber_number)s'."
            ),
            code="invalid",
            params={"subscriber_number": subscriber_number},
        )
    if not subscriber_number.isdigit():
        raise ValidationError(
            _(
                "E.164 phone number must have a valid subscriber number, got '%(subscriber_number)s'"
            ),
            code="invalid",
            params={"subscriber_number": subscriber_number},
        )
