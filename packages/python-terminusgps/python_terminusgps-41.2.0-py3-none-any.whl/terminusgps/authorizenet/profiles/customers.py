from authorizenet import apicontractsv1, apicontrollers

from terminusgps.authorizenet.auth import get_merchant_auth
from terminusgps.authorizenet.controllers import execute_controller

__all__ = [
    "create_customer_profile",
    "delete_customer_profile",
    "get_customer_profile",
    "get_customer_profile_ids",
    "update_customer_profile",
]


def create_customer_profile(merchant_id: int | str, email: str, description: str = ""):
    """
    `createCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-create-customer-profile>`_.

    :param merchant_id: A merchant designated customer id.
    :type merchant_id: :py:obj:`int` | :py:obj:`str`
    :param email: A customer email address.
    :type email: :py:obj:`str`
    :param description: An optional customer description.
    :type description: :py:obj:`str`
    :returns: An Authorizenet createCustomerProfile response.
    :rtype: :py:obj:`dict`

    """
    request = apicontractsv1.createCustomerProfileRequest(
        merchantAuthentication=get_merchant_auth(),
        profile=apicontractsv1.customerProfileType(
            merchantCustomerId=str(merchant_id), description=description, email=email
        ),
    )
    return execute_controller(apicontrollers.createCustomerProfileController(request))


def get_customer_profile(customer_profile_id: int, include_issuer_info: bool = False):
    """
    `getCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-get-customer-profile>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :param include_issuer_info: Whether or not to include issuer info in the response. Default is :py:obj:`False`.
    :type include_issuer_info: :py:obj:`bool`
    :returns: An Authorizenet getCustomerProfile response.
    :rtype: :py:obj:`dict`

    """
    request = apicontractsv1.getCustomerProfileRequest(
        merchantAuthentication=get_merchant_auth(),
        customerProfileId=str(customer_profile_id),
        includeIssuerInfo=str(include_issuer_info).lower(),
    )
    return execute_controller(apicontrollers.getCustomerProfileController(request))


def get_customer_profile_ids():
    """
    `getCustomerProfileIdsRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-get-customer-profile-ids>`_.

    :returns: An Authorizenet getCustomerProfileIds response.
    :rtype: :py:obj:`dict`

    """
    request = apicontractsv1.getCustomerProfileIdsRequest(
        merchantAuthentication=get_merchant_auth()
    )
    return execute_controller(apicontrollers.getCustomerProfileIdsController(request))


def update_customer_profile(
    customer_profile_id: int, new_profile: apicontractsv1.customerProfileExType
):
    """
    `updateCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-update-customer-profile>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :param new_profile: An Authorizenet customer profile ex object.
    :type new_profile: :py:obj:`~authorizenet.apicontractsv1.customerProfileExType`
    :returns: An Authorizenet updateCustomerProfile response.
    :rtype: :py:obj:`dict`

    """
    new_profile.customerProfileId = str(customer_profile_id)
    request = apicontractsv1.updateCustomerProfileRequest(
        merchantAuthentication=get_merchant_auth(), profile=new_profile
    )
    return execute_controller(apicontrollers.updateCustomerProfileController(request))


def delete_customer_profile(customer_profile_id: int):
    """
    `deleteCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-delete-customer-profile>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :returns: An Authorizenet deleteCustomerProfile response.
    :rtype: :py:obj:`dict`

    """
    request = apicontractsv1.deleteCustomerProfileRequest(
        merchantAuthentication=get_merchant_auth(),
        customerProfileId=str(customer_profile_id),
    )
    return execute_controller(apicontrollers.deleteCustomerProfileController(request))
