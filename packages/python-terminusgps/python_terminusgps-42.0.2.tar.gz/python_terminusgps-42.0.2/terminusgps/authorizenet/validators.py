import calendar
import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_credit_card_number(value: str) -> None:
    """
    Raises :py:exc:`~django.core.exceptions.ValidationError` if the value is an invalid credit card number.

    Uses the `Luhn algorithm <https://en.wikipedia.org/wiki/Luhn_algorithm>`_ to validate the credit card number.

    :param value: A credit card number string.
    :type value: :py:obj:`str`
    :raises ValidationError: If the value contains non-digit characters.
    :raises ValidationError: If the value fails the Luhn algorithm.
    :returns: Nothing.
    :rtype: :py:obj:`None`

    """
    if not value.isdigit():
        raise ValidationError(
            _("Credit card number can only contain digits. Got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )

    card_number = [int(num) for num in reversed(value)]
    even_digits = card_number[1::2]
    odd_digits = card_number[0::2]

    checksum = 0
    checksum += sum(
        [digit * 2 if digit * 2 <= 9 else (digit * 2) % 9 or 9 for digit in even_digits]
    )
    checksum += sum([digit for digit in odd_digits])

    if checksum % 10 != 0:
        raise ValidationError(_("Invalid credit card number."), code="invalid")


def validate_credit_card_expiry_month(value: str) -> None:
    """
    Raises :py:exc:`~django.core.exceptions.ValidationError` if the value is an invalid credit card expiration date month.

    :param value: A credit card expiration year string.
    :type value: :py:obj:`str`
    :raises ValidationError: If the value contains non-digit characters.
    :raises ValidationError: If the value is negative.
    :raises ValidationError: If the value isn't between 1-12.
    :returns: Nothing.
    :rtype: :py:obj:`None`

    """
    if not value.isdigit():
        raise ValidationError(
            _("Expiration month can only contain digits, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )
    if not int(value) > 0:
        raise ValidationError(
            _("Expiration month can only be a positive value, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )

    try:
        calendar.Month(int(value))
    except ValueError:
        raise ValidationError(
            _("Expiration month must be between 1-12, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )


def validate_credit_card_expiry_year(value: str) -> None:
    """
    Raises :py:exc:`~django.core.exceptions.ValidationError` if the value is an invalid credit card expiration date year.

    :param value: A credit card expiration year string.
    :type value: :py:obj:`str`
    :raises ValidationError: If the value contains non-digit characters.
    :raises ValidationError: If the value is negative.
    :raises ValidationError: If the value is a year in the past.
    :returns: Nothing.
    :rtype: :py:obj:`None`

    """
    if not value.isdigit():
        raise ValidationError(
            _("Expiration year can only contain digits, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )
    if not int(value) > 0:
        raise ValidationError(
            _("Expiration year can only be a positive value, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )

    input_year = datetime.datetime.strptime(value, "%y").year
    this_year = datetime.datetime.now().year

    if not input_year >= this_year:
        raise ValidationError(
            _("Expiration year cannot be in the past, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )
