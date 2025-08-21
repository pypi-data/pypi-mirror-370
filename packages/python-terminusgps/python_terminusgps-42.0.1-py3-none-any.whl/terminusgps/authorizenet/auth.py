from authorizenet.apicontractsv1 import merchantAuthenticationType
from django.conf import settings

from terminusgps.django import settings as default_settings

if not settings.configured:
    settings.configure(default_settings)


def get_merchant_auth() -> merchantAuthenticationType:
    """
    Returns the current merchant authentication information for Authorizenet API requests.

    :returns: A merchant authentication object.
    :rtype: :py:obj:`~authorizenet.apicontractsv1.merchantAuthenticationType`

    """
    return merchantAuthenticationType(
        name=str(settings.MERCHANT_AUTH_LOGIN_ID),
        transactionKey=str(settings.MERCHANT_AUTH_TRANSACTION_KEY),
    )


def get_environment() -> str:
    """
    Returns the current environment for Authorizenet API requests.

    :returns: An Authorizenet API environment string.
    :rtype: :py:obj:`str`

    """
    return settings.MERCHANT_AUTH_ENVIRONMENT


def get_validation_mode() -> str:
    """
    Returns the current validation mode for Authorizenet API requests.

    :returns: An Authorizenet API validation string.
    :rtype: :py:obj:`str`

    """
    return settings.MERCHANT_AUTH_VALIDATION_MODE
