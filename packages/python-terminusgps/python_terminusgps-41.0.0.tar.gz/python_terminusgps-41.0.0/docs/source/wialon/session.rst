Wialon API Sessions
===================

.. autoclass:: terminusgps.wialon.session.WialonSession
   :members:
   :class-doc-from: init
   :autoclasstoc:


=====
Usage
=====

.. code:: python

    from terminusgps.wialon.session import WialonSession

    # Create a session and login to it
    session = WialonSession()
    session.login(token="my_secure_token")

    # Use the logged in session to perform API actions
    session.wialon_api.core_search_item(**{"id": "123", "flags": 1})

    # Don't forget to logout of the session
    # Sessions are destroyed after 5min of inactivity
    session.logout()

    # Alternatively, use a context manager
    # The context manager handles logging in and out of the session.
    with WialonSession() as session:
        session.wialon_api.core_search_item(**{"id": "123", "flags": 1})

    # If you already have a session id, no need to login again
    session = WialonSession(sid="my_valid_session_id")
    session.wialon_api.core_search_item(**{"id": "123", "flags": 1})
