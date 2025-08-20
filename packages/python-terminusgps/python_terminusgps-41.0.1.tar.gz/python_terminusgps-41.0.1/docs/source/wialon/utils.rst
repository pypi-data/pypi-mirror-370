Utilities
=========

=========
Functions
=========

.. automodule:: terminusgps.wialon.utils
   :members:

=====
Usage
=====

.. code:: python

    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.utils import get_id_from_iccid, generate_wialon_password

    # Generate random Wialon compliant passwords
    password_0 = generate_wialon_password(16)
    password_1 = generate_wialon_password(32)
    password_2 = generate_wialon_password(64)

    # Retrieve unit id from IMEI #
    with WialonSession() as session:
        unit_id = get_id_from_imei("869084062183235", session=session)
        print(f"{unit_id = }") # unit_id = 28006231
