import datetime
import decimal

from authorizenet import apicontractsv1, apicontrollers
from django import forms
from django.conf import settings

from .auth import get_merchant_auth
from .controllers import AuthorizenetControllerExecutor


def calculate_amount_plus_tax(
    amount: decimal.Decimal, tax_rate: decimal.Decimal | None = None
) -> decimal.Decimal:
    """
    Returns the amount + tax. Uses :confval:`DEFAULT_TAX_RATE` if ``tax_rate`` wasn't provided.

    :param amount: Amount to add tax to.
    :type amount: :py:obj:`~decimal.Decimal`
    :param tax_rate: A tax rate to use in the calculation.
    :type tax_rate: :py:obj:`~decimal.Decimal` | :py:obj:`None`
    :returns: The amount + tax.
    :rtype: :py:obj:`~decimal.Decimal`

    """
    if tax_rate is None:
        tax_rate = settings.DEFAULT_TAX_RATE
    return round(amount * (1 + tax_rate), ndigits=2)


def get_merchant_details() -> dict | None:
    """
    Returns Authorizenet merchant details.

    `getMerchantDetailsRequest <http://developer.authorize.net/api/reference/index.html#transaction-reporting-get-merchant-details>`_

    :raises AuthorizenetControllerExecutionError: If the API call fails.
    :returns: A merchant details object, if found.
    :rtype: :py:obj:`dict` | :py:obj:`None`

    """
    request = apicontractsv1.getMerchantDetailsRequest(
        merchantAuthentication=get_merchant_auth()
    )
    controller = apicontrollers.getMerchantDetailsController(request)
    return AuthorizenetControllerExecutor.execute_controller(controller)


def get_transaction(id: int | str) -> dict | None:
    """
    Returns Authorizenet transaction details by id.

    `getTransactionDetailsRequest <https://developer.authorize.net/api/reference/index.html#transaction-reporting-get-transaction-details>`_

    :param id: An Authorizenet transaction id.
    :type id: :py:obj:`int` | :py:obj:`str`
    :raises ValueError: If ``id`` was provided as a string containing non-digits.
    :raises AuthorizenetControllerExecutionError: If the API call fails.
    :returns: A transaction object, if found.
    :rtype: :py:obj:`dict` | :py:obj:`None`

    """
    if isinstance(id, str) and not id.isdigit():
        raise ValueError(f"'id' can only contain digits, got '{id}'.")

    request = apicontractsv1.getTransactionDetailsRequest(
        merchantAuthentication=get_merchant_auth(), transId=str(id)
    )
    controller = apicontrollers.getTransactionDetailsController(request)
    return AuthorizenetControllerExecutor.execute_controller(controller)


def generate_monthly_subscription_schedule(
    start_date: datetime.date, total_occurrences: int = 9999, trial_occurrences: int = 0
) -> apicontractsv1.paymentScheduleType:
    return apicontractsv1.paymentScheduleType(
        interval=apicontractsv1.paymentScheduleTypeInterval(
            length=1, unit=apicontractsv1.ARBSubscriptionUnitEnum.months
        ),
        startDate=f"{start_date:%Y-%m-%d}",
        totalOccurrences=str(total_occurrences),
        trialOccurrences=str(trial_occurrences),
    )


def get_customer_profile_ids() -> list[int]:
    """
    Returns a list of all customer profile ids in Authorizenet.

    :raises AuthorizenetControllerExecutionError: If the API call fails.
    :returns: A list of all customer profile ids in Authorizenet.
    :rtype: :py:obj:`list`

    """
    request = apicontractsv1.getCustomerProfileIdsRequest(
        merchantAuthentication=get_merchant_auth()
    )
    controller = apicontrollers.getCustomerProfileIdsController(request)
    response = AuthorizenetControllerExecutor.execute_controller(controller)
    if response is None or "ids" not in response.getchildren():
        return []
    return [int(id) for id in response.ids.getchildren()]


def generate_customer_address(form: forms.Form) -> apicontractsv1.customerAddressType:
    """
    Takes a form and returns a :py:obj:`~authorizenet.apicontractsv1.customerAddressType`.

    Required form fields:

    +----------------+------------------------------------------------------------+
    | name           | type                                                       |
    +================+============================================================+
    | ``address``    | :py:obj:`~authorizenet.apicontractsv1.customerAddressType` |
    +----------------+------------------------------------------------------------+
    | ``first_name`` | :py:obj:`str`                                              |
    +----------------+------------------------------------------------------------+
    | ``last_name``  | :py:obj:`str`                                              |
    +----------------+------------------------------------------------------------+

    :param form: A Django form.
    :type form: :py:obj:`~django.forms.Form`
    :raises ValueError: If ``address`` wasn't in the form.
    :raises ValueError: If ``first_name`` wasn't in the form.
    :raises ValueError: If ``last_name`` wasn't in the form.
    :returns: A customer address object.
    :rtype: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`

    """
    required_fields: list[str] = ["address", "first_name", "last_name"]
    for field in required_fields:
        if field not in form.cleaned_data or form.cleaned_data.get(field) is None:
            raise ValueError(
                f"'{field}' was not provided by the form, got '{form.cleaned_data.get(field)}'."
            )

    address: apicontractsv1.customerAddressType = form.cleaned_data["address"]
    address.firstName = form.cleaned_data["first_name"]
    address.lastName = form.cleaned_data["last_name"]
    if form.cleaned_data.get("phone"):
        address.phone = form.cleaned_data["phone"]
    return address


def generate_customer_payment(form: forms.Form) -> apicontractsv1.paymentType:
    """
    Takes a form and returns a :py:obj:`~authorizenet.apicontractsv1.paymentType`.

    Required form fields:

    +-----------------+-------------------------------------------------------+
    | name            | type                                                  |
    +=================+=======================================================+
    | ``credit_card`` | :py:obj:`~authorizenet.apicontractsv1.creditCardType` |
    +-----------------+-------------------------------------------------------+

    :param form: A Django form.
    :type form: :py:obj:`~django.forms.Form`
    :raises ValueError: If ``credit_card`` wasn't in the form.
    :returns: A payment object.
    :rtype: :py:obj:`~authorizenet.apicontractsv1.paymentType`

    """
    required_fields: list[str] = ["credit_card"]
    for field in required_fields:
        if field not in form.cleaned_data or form.cleaned_data.get(field) is None:
            raise ValueError(
                f"'{field}' was not provided by the form, got '{form.cleaned_data.get(field)}'."
            )

    credit_card: apicontractsv1.creditCardType = form.cleaned_data["credit_card"]
    return apicontractsv1.paymentType(creditCard=credit_card)
