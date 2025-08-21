Usage Examples
==============

=========================================
Retrieve an Authorizenet customer profile
=========================================

--------------------------------------------------------------------------------
1. Import :py:obj:`~terminusgps.authorizenet.profiles.customers.CustomerProfile`
--------------------------------------------------------------------------------

.. code:: python

    from terminusgps.authorizenet.profiles import CustomerProfile

----------------------------------------------------------------------
2. Initialize a profile with an id, a merchant id or an email address.
----------------------------------------------------------------------

.. code:: python

    ...
    # All of these would retrieve the same customer profile
    cprofile = CustomerProfile(id=1)
    cprofile = CustomerProfile(merchant_id=0)
    cprofile = CustomerProfile(email="email@domain.com")

------------------------------------------------
3. Perform operations using the customer profile
------------------------------------------------

.. code:: python

    ...
    cprofile.update(email="support@terminusgps.com", desc="Support User")
    print(cprofile.email) # "support@terminusgps.com"

-----------------
Full code example
-----------------

.. code:: python

    from terminusgps.authorizenet.profiles import CustomerProfile

    cprofile = CustomerProfile(id=1)
    cprofile.update(email="support@terminusgps.com", desc="Support User")
    print(cprofile.email) # "support@terminusgps.com"

=======================================
Create an Authorizenet customer profile
=======================================

--------------------------------------------------------------------------------
1. Import :py:obj:`~terminusgps.authorizenet.profiles.customers.CustomerProfile`
--------------------------------------------------------------------------------

.. code:: python

    from terminusgps.authorizenet.profiles import CustomerProfile

------------------------------------------------------------------------
2. Initialize a customer profile with a merchant id or an email address.
------------------------------------------------------------------------

.. code:: python

    ...
    cprofile = CustomerProfile(email="sales@terminusgps.com")
    print(cprofile.id) # "123"

-----------------
Full code example
-----------------

.. code:: python

    from terminusgps.authorizenet.profiles import CustomerProfile

    cprofile = CustomerProfile(email="sales@terminusgps.com")
    print(cprofile.id) # "123"

=======================================================
Create an Authorizenet payment profile with credit card
=======================================================

----------------------------
1. Import relevant profiles.
----------------------------

.. code:: python

    from authorizenet import apicontractsv1
    from terminusgps.authorizenet.profiles import CustomerProfile, PaymentProfile

------------------------------
2. Initialize profile objects.
------------------------------

.. code:: python

    ...
    cprofile = CustomerProfile(id=1)
    pprofile = PaymentProfile(customer_profile_id=cprofile.id, id=None, default=True)
    
-------------------------------------------------------------------------------------------------------------------------------------------------
3. Execute :py:meth:`~terminusgps.authorizenet.profiles.payments.PaymentProfile.create` with an address and payment object and save its response.
-------------------------------------------------------------------------------------------------------------------------------------------------

.. code:: python

    ...
    address_obj = apicontractsv1.customerAddressType(
        firstName="TestFirst",
        lastName="TestLast",
        company="TestCompany",
        address="123 Main St",
        city="Houston",
        state="TX",
        zip="77065",
        country="US",
    ) 
    payment_obj = apicontractsv1.paymentType(
        creditCard=apicontractsv1.creditCardType(
            cardNumber="4111111111111111",
            expirationDate="04-39",
            cardCode="444",
        )
    )

    pprofile.id = pprofile.create(address_obj, payment_obj)
    print(pprofile.last_4) # "1111"

-----------------
Full code example
-----------------

.. code:: python

    from authorizenet import apicontractsv1
    from terminusgps.authorizenet.profiles import CustomerProfile, PaymentProfile

    cprofile = CustomerProfile(id=1)
    pprofile = PaymentProfile(customer_profile_id=cprofile.id, id=None, default=True)

    address_obj = apicontractsv1.customerAddressType(
        firstName="TestFirst",
        lastName="TestLast",
        company="TestCompany",
        address="123 Main St",
        city="Houston",
        state="TX",
        zip="77065",
        country="US",
    ) 
    payment_obj = apicontractsv1.paymentType(
        creditCard=apicontractsv1.creditCardType(
            cardNumber="4111111111111111",
            expirationDate="04-39",
            cardCode="444",
        )
    )

    pprofile.id = pprofile.create(address_obj, payment_obj)
    print(pprofile.last_4) # "1111"
