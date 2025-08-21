from authorizenet import apicontractsv1, apicontrollers

from terminusgps.authorizenet.auth import get_merchant_auth, get_validation_mode
from terminusgps.authorizenet.controllers import execute_controller

__all__ = [
    "create_customer_payment_profile",
    "delete_customer_payment_profile",
    "get_customer_payment_profile",
    "update_customer_payment_profile",
    "validate_customer_payment_profile",
]


def create_customer_payment_profile(
    customer_profile_id: int,
    new_payment_profile: apicontractsv1.customerPaymentProfileType,
):
    """
    `createCustomerPaymentProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-create-customer-payment-profile>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :param new_payment_profile: An Authorizenet payment profile object.
    :type new_payment_profile: :py:obj:`~authorizenet.apicontractsv1.customerPaymentProfileType`
    :returns: An Authorizenet createCustomerPaymentProfile response.
    :rtype: :py:obj:`dict`

    """
    request = apicontractsv1.createCustomerPaymentProfileRequest(
        merchantAuthentication=get_merchant_auth(),
        customerProfileId=str(customer_profile_id),
        paymentProfile=new_payment_profile,
        validationMode=get_validation_mode(),
    )
    return execute_controller(
        apicontrollers.createCustomerPaymentProfileController(request)
    )


def get_customer_payment_profile(
    customer_profile_id: int,
    customer_payment_profile_id: int,
    include_issuer_info: bool = False,
):
    """
    `getCustomerPaymentProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-get-customer-payment-profile>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :param customer_payment_profile_id: An Authorizenet customer payment profile id.
    :type customer_payment_profile_id: :py:obj:`int`
    :param include_issuer_info: Whether or not to include issuer info in the response. Default is :py:obj:`False`.
    :type include_issuer_info: :py:obj:`bool`
    :returns: An Authorizenet getCustomerPaymentProfile response.
    :rtype: :py:obj:`dict`

    """
    request = apicontractsv1.getCustomerPaymentProfileRequest(
        merchantAuthentication=get_merchant_auth(),
        customerProfileId=str(customer_profile_id),
        customerPaymentProfileId=str(customer_payment_profile_id),
        includeIssuerInfo=str(include_issuer_info).lower(),
    )
    return execute_controller(
        apicontrollers.getCustomerPaymentProfileController(request)
    )


def validate_customer_payment_profile(
    customer_profile_id: int, customer_payment_profile_id: int
):
    """
    `validateCustomerPaymentProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-validate-customer-payment-profile>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :param customer_payment_profile_id: An Authorizenet customer payment profile id.
    :type customer_payment_profile_id: :py:obj:`int`
    :returns: An Authorizenet validateCustomerPaymentProfile response.
    :rtype: :py:obj:`dict`

    """
    request = apicontractsv1.validateCustomerPaymentProfileRequest(
        merchantAuthentication=get_merchant_auth(),
        customerProfileId=str(customer_profile_id),
        customerPaymentProfileId=str(customer_payment_profile_id),
        validationMode=get_validation_mode(),
    )
    return execute_controller(
        apicontrollers.validateCustomerPaymentProfileController(request)
    )


def update_customer_payment_profile(
    customer_profile_id: int,
    customer_payment_profile_id: int,
    new_payment_profile: apicontractsv1.customerPaymentProfileType,
):
    """
    `updateCustomerPaymentProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-update-customer-payment-profile>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :param customer_payment_profile_id: An Authorizenet customer payment profile id.
    :type customer_payment_profile_id: :py:obj:`int`
    :param new_payment_profile: An Authorizenet payment profile object.
    :type new_payment_profile: :py:obj:`~authorizenet.apicontractsv1.customerPaymentProfileType`
    :returns: An Authorizenet updateCustomerPaymentProfile response.
    :rtype: :py:obj:`dict`

    """
    new_payment_profile.customerPaymentProfileId = str(customer_payment_profile_id)
    request = apicontractsv1.updateCustomerPaymentProfileRequest(
        merchantAuthentication=get_merchant_auth(),
        customerProfileId=str(customer_profile_id),
        paymentProfile=new_payment_profile,
        validationMode=get_validation_mode(),
    )
    return execute_controller(
        apicontrollers.updateCustomerPaymentProfileController(request)
    )


def delete_customer_payment_profile(
    customer_profile_id: int, customer_payment_profile_id: int
):
    """
    `deleteCustomerPaymentProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-delete-customer-payment-profile>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :param customer_payment_profile_id: An Authorizenet customer payment profile id.
    :type customer_payment_profile_id: :py:obj:`int`
    :returns: An Authorizenet deleteCustomerPaymentProfile response.
    :rtype: :py:obj:`dict`

    """
    request = apicontractsv1.deleteCustomerPaymentProfileRequest(
        merchantAuthentication=get_merchant_auth(),
        customerProfileId=str(customer_profile_id),
        customerPaymentProfileId=str(customer_payment_profile_id),
    )
    return execute_controller(
        apicontrollers.deleteCustomerPaymentProfileController(request)
    )
