from authorizenet import apicontractsv1, apicontrollers

from terminusgps.authorizenet.auth import get_merchant_auth
from terminusgps.authorizenet.controllers import execute_controller

__all__ = [
    "create_customer_shipping_address",
    "delete_customer_shipping_address",
    "get_customer_shipping_address",
    "update_customer_shipping_address",
]


def create_customer_shipping_address(
    customer_profile_id: int,
    new_address: apicontractsv1.customerAddressType,
    default: bool = True,
):
    """
    `createCustomerShippingAddressRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-create-customer-shipping-address>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :param new_address: An Authorizenet customer address object.
    :type new_address: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
    :param default: Whether or not to mark the new shipping address as default. Default is :py:obj:`True`.
    :type default: :py:obj:`bool`
    :returns: An Authorizenet createCustomerShippingAddress response.
    :rtype: :py:obj:`dict`

    """
    request = apicontractsv1.createCustomerShippingAddressRequest(
        merchantAuthentication=get_merchant_auth(),
        customerProfileId=str(customer_profile_id),
        address=new_address,
        defaultShippingAddress=str(default).lower(),
    )
    return execute_controller(
        apicontrollers.createCustomerShippingAddressController(request)
    )


def get_customer_shipping_address(
    customer_profile_id: int, customer_address_profile_id: int
):
    """
    `getCustomerShippingAddressRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-get-customer-shipping-address>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :param customer_address_profile_id: An Authorizenet customer address profile id.
    :type customer_address_profile_id: :py:obj:`int`
    :returns: An Authorizenet getCustomerShippingAddress response.
    :rtype: :py:obj:`dict`

    """
    request = apicontractsv1.getCustomerShippingAddressRequest(
        merchantAuthentication=get_merchant_auth(),
        customerProfileId=str(customer_profile_id),
        customerAddressId=str(customer_address_profile_id),
    )
    return execute_controller(
        apicontrollers.getCustomerShippingAddressController(request)
    )


def update_customer_shipping_address(
    customer_profile_id: int,
    new_address: apicontractsv1.customerAddressType,
    default: bool = False,
):
    """
    `updateCustomerShippingAddressRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-update-customer-shipping-address>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :param new_address: An Authorizenet customer address object.
    :type new_address: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
    :param default: Whether or not to mark the new shipping address as default. Default is :py:obj:`False`.
    :type default: :py:obj:`bool`
    :returns: An Authorizenet updateCustomerShippingAddress response.
    :rtype: :py:obj:`dict`

    """
    request = apicontractsv1.updateCustomerShippingAddressRequest(
        merchantAuthentication=get_merchant_auth(),
        customerProfileId=str(customer_profile_id),
        address=new_address,
        defaultShippingAddress=str(default).lower(),
    )
    return execute_controller(
        apicontrollers.updateCustomerShippingAddressController(request)
    )


def delete_customer_shipping_address(
    customer_profile_id: int, customer_address_profile_id: int
):
    """
    `deleteCustomerShippingAddressRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-delete-customer-shipping-address>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: :py:obj:`int`
    :param customer_address_profile_id: An Authorizenet customer address profile id.
    :type customer_address_profile_id: :py:obj:`int`
    :returns: An Authorizenet deleteCustomerShippingAddress response.
    :rtype: :py:obj:`dict`

    """
    request = apicontractsv1.deleteCustomerShippingAddressRequest(
        merchantAuthentication=get_merchant_auth(),
        customerProfileId=str(customer_profile_id),
        customerAddressId=str(customer_address_profile_id),
    )
    return execute_controller(
        apicontrollers.deleteCustomerShippingAddressController(request)
    )
