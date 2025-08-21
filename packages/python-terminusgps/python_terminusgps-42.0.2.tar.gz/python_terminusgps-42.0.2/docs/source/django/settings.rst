Settings
========

.. attention:: These settings must be set in your Django project's settings module for Terminus GPS SDKs to operate properly.

.. confval:: DEBUG

    :type: :py:obj:`bool`
    :default: :py:obj:`True`

    Debug mode enabled.

.. confval:: MERCHANT_AUTH_LOGIN_ID

    :type: :py:obj:`str`

    An authorizenet merchant authentication login id.

.. confval:: MERCHANT_AUTH_TRANSACTION_KEY

    :type: :py:obj:`str`

    An authorizenet merchant authentication transaction key.

    This key signs all Authorizenet transactions.

.. confval:: TWILIO_FROM_NUMBER

    :type: :py:obj:`str`

    A phone number to send Twilio notifications from.

.. confval:: TWILIO_MESSAGING_SID

    :type: :py:obj:`str`

    A Twilio API messaging session id.

.. confval:: TWILIO_SID

    :type: :py:obj:`str`

    A Twilio API session id.

.. confval:: TWILIO_TOKEN

    :type: :py:obj:`str`

    A Twilio API token.

.. confval:: WIALON_ADMIN_ID

    :type: :py:obj:`str`

    A Wialon user id to operate as during Wialon API session.

.. confval:: WIALON_TOKEN

    :type: :py:obj:`str`

    An active Wialon API token.
