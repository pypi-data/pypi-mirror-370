Usage Examples
==============

===============================
Create a new user and rename it
===============================

----------------------------------------------------------------------------------------------------------
1. Open a :py:obj:`~terminusgps.wialon.session.WialonSession` as a context manager and instantiate a user.
----------------------------------------------------------------------------------------------------------

Let's also import :py:obj:`~terminusgps.wialon.utils.generate_wialon_password` so we don't have to come up with a valid Wialon password ourselves.

.. code:: python

    from terminusgps.wialon.items import WialonUser
    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.utils import generate_wialon_password

    with WialonSession(token="my-secure-wialon-token") as session:
        user = WialonUser(
            id=None,
            session=session,
            creator_id="27884511", # Admin user id
            name="test_user",
            password=generate_wialon_password(32)
        )
        print(f"{user.name = }") # user.name = "test_user"

.. seealso:: :py:meth:`~terminusgps.wialon.items.user.WialonUser.create` for details on initializing a user.

--------------------------------------------------------------------------------------------------------------
2. Execute :py:meth:`~terminusgps.wialon.items.base.WialonBase.rename` on the unit within the session context.
--------------------------------------------------------------------------------------------------------------

Calling :py:meth:`~terminusgps.wialon.items.base.WialonBase.rename` renames the unit in Wialon and updates its :py:attr:`name` attribute.

.. code:: python

    from terminusgps.wialon.items import WialonUser
    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.utils import generate_wialon_password

    with WialonSession(token="my-secure-wialon-token") as session:
        ...
        unit.rename("super_test_user")
        print(f"{user.name = }") # user.name = "super_test_user"
        # Session is logged out after exiting scope

-----------------
Full code example
-----------------

.. code:: python

    from terminusgps.wialon.items import WialonUnit
    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.utils import generate_wialon_password

    with WialonSession(token="my-secure-wialon-token") as session:
        unit = WialonUnit(
            id=None,
            session=session,
            creator_id="123",
            name="test_user",
            password=generate_wialon_password(32)
        )
        print(f"{unit.name = }") # user.name = "test_user"
        unit.rename("super_test_user")
        print(f"{unit.name = }") # user.name = "super_test_user"
        # Session is logged out after exiting scope


============================================
Create an account and migrate a unit into it
============================================

-------------------------------------
1. Create a new user for the account.
-------------------------------------

If you choose to use an already existing user for this process, you may need to pass ``skip_creator_check=True`` when creating the resource in the next step.

This is because Wialon `forbids users from creating accounts if they are already responsible for creating other Wialon objects <https://sdk.wialon.com/wiki/en/sidebar/remoteapi/apiref/core/create_resource>`_.

.. code:: python

    from terminusgps.wialon import constants
    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import (
        WialonResource, WialonUnit, WialonUser
    )

    with WialonSession(token="my-secure-wialon-token") as session:
        account_user = WialonUser(
            id=None,
            session=session,
            creator_id="27884511", # Admin user id
            name="account_user",
            password="super_secure_password1!",
        )

.. seealso:: :py:meth:`~terminusgps.wialon.items.user.WialonUser.create` for details on initializing a user.

--------------------------------------------------------------
2. Create a new resource with the account user as its creator.
--------------------------------------------------------------

.. code:: python

    from terminusgps.wialon import constants
    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import (
        WialonResource, WialonUnit, WialonUser
    )

    with WialonSession(token="my-secure-wialon-token") as session:
        ...
        account_resource = WialonResource(
            id=None,
            session=session,
            creator_id=account_user.id,
            name="account_resource",
        )

.. seealso:: :py:meth:`~terminusgps.wialon.items.resource.WialonResource.create` for details on initializing a resource.

------------------------------------------------------------------
3. Retrieve a :py:obj:`~terminusgps.wialon.items.unit.WialonUnit`.
------------------------------------------------------------------

.. code:: python

    from terminusgps.wialon import constants
    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import (
        WialonResource, WialonUnit, WialonUser
    )

    with WialonSession(token="my-secure-wialon-token") as session:
        ...
        unit = WialonUnit(id="12345678", session=session)

.. seealso:: :py:meth:`~terminusgps.wialon.items.unit.WialonUnit.create` for details on initializing a unit.

------------------------------------------------
4. Grant the account user migration permissions.
------------------------------------------------

:py:meth:`~terminusgps.wialon.items.user.WialonUser.grant_access` grants a user access to a unit using an access mask.

:py:obj:`~terminusgps.wialon.constants.ACCESSMASK_UNIT_MIGRATION` is an access mask that contains all required permissions migrating a unit into an account.

If you don't grant `these permissions <https://sdk.wialon.com/wiki/en/sidebar/remoteapi/apiref/account/change_account>`_ to the account user, the next steps may fail.

.. code:: python

    from terminusgps.wialon import constants
    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import (
        WialonResource, WialonUnit, WialonUser
    )

    with WialonSession(token="my-secure-wialon-token") as session:
        ...
        account_user.grant_access(unit, access_mask=constants.ACCESSMASK_UNIT_MIGRATION)

--------------------------------------------------------
5. Transform the resource into an account and enable it.
--------------------------------------------------------

A :py:obj:`~terminusgps.wialon.items.resource.WialonResource` can be turned into a Wialon account by calling :py:meth:`~terminusgps.wialon.items.resource.WialonResource.create_account`.

:py:meth:`~terminusgps.wialon.items.resource.WialonResource.enable_account` **must** be called at some point because a disabled account cannot migrate units into itself.

.. code:: python

    from terminusgps.wialon import constants
    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import (
        WialonResource, WialonUnit, WialonUser
    )

    with WialonSession(token="my-secure-wialon-token") as session:
        ...
        account_resource.create_account("terminusgps_ext_hist")
        account_resource.enable_account()

-------------------------------------
6. Migrate the unit into the account.
-------------------------------------

Finally, pass the unit into :py:meth:`~terminusgps.wialon.items.resource.WialonResource.migrate_unit` to finish unit migration.

.. code:: python

    from terminusgps.wialon import constants
    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import (
        WialonResource, WialonUnit, WialonUser
    )

    with WialonSession(token="my-secure-wialon-token") as session:
        ...
        account_resource.migrate_unit(unit)

-----------------
Full code example
-----------------

.. code:: python

    from terminusgps.wialon import constants
    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import (
        WialonResource, WialonUnit, WialonUser
    )

    with WialonSession(token="my-secure-wialon-token") as session:
        account_user = WialonUser(
            id=None,
            session=session,
            creator_id="27884511", # Admin user id
            name="account_user",
            password="super_secure_password1!",
        )
        account_resource = WialonResource(
            id=None,
            session=session,
            creator_id=account_user.id,
            name="account_resource",
        )
        unit = WialonUnit(id="12345678", session=session)
        account_user.grant_access(unit, access_mask=constants.ACCESSMASK_UNIT_MIGRATION)
        account_resource.create_account("terminusgps_ext_hist")
        account_resource.enable_account()
        account_resource.migrate_unit(unit)

==========================
Add a driver to a resource
==========================

-----------------------
1. Retrieve a resource.
-----------------------

.. code:: python

    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import WialonResource

    with WialonSession(token="my-secure-wialon-token") as session:
        resource = WialonResource(id="12345678", session=session)

-----------------------------------------------------------------------------------
2. Call :py:meth:`~terminusgps.wialon.items.resource.WialonResource.create_driver`.
-----------------------------------------------------------------------------------

.. code:: python

    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import WialonResource

    with WialonSession(token="my-secure-wialon-token") as session:
        ...
        resource.create_driver(
            name="test_driver",
            code="1234",
            desc="A test driver.",
            phone="+15555555555",
            mobile_auth_code="1234",
            custom_fields={"my_field_key": "my_field_value"}
        )

-----------------
Full code example
-----------------

.. code:: python

    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import WialonResource

    with WialonSession(token="my-secure-wialon-token") as session:
        resource = WialonResource(id="12345678", session=session)
        resource.create_driver(
            name="test_driver",
            code="1234",
            desc="A test driver.",
            phone="+15555555555",
            mobile_auth_code="1234",
            custom_fields={"my_field_key": "my_field_value"}
        )

========================================
Update a unit's "to_number" custom field
========================================

------------------------------------------------------------------
1. Retrieve a :py:obj:`~terminusgps.wialon.items.unit.WialonUnit`.
------------------------------------------------------------------

.. code:: python

    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import WialonUnit

    with WialonSession(token="my-secure-wialon-token") as session:
        unit = WialonUnit(id="12345678", session=session)

---------------------------------------------------------------------------
2. Call :py:meth:`~terminusgps.wialon.items.base.WialonBase.update_cfield`.
---------------------------------------------------------------------------

If the custom field doesn't exist in Wialon yet, it will be created by :py:meth:`~terminusgps.wialon.items.base.WialonBase.update_cfield`.

.. code:: python

    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import WialonUnit

    with WialonSession(token="my-secure-wialon-token") as session:
        ...
        unit.update_cfield(key="to_number", value="+15555555555")
        print(f"{unit.cfields['to_number'] = }") # unit.cfields["to_number"] = "+15555555555"

-----------------
Full code example
-----------------

.. code:: python

    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import WialonUnit

    with WialonSession(token="my-secure-wialon-token") as session:
        unit = WialonUnit(id="12345678", session=session)
        unit.update_cfield(key="to_number", value="+15555555555")
        print(f"{unit.cfields['to_number'] = }") # unit.cfields["to_number"] = "+15555555555"
