Forms
=====

--------
Renderer
--------

.. autoclass:: terminusgps.django.forms.renderer.TerminusgpsFormRenderer
    :members:

------
Fields
------

.. autoclass:: terminusgps.django.forms.fields.AddressField
    :members:

.. autoclass:: terminusgps.django.forms.fields.CreditCardField
    :members:

-------
Widgets
-------

.. autoclass:: terminusgps.django.forms.widgets.AddressWidget
    :members:

.. autoclass:: terminusgps.django.forms.widgets.CreditCardWidget
    :members:

-----
Usage
-----

.. code:: python

    from django import forms
    from terminusgps.django.forms import AddressField, CreditCardField

    class MyCustomForm(forms.Form):
        first_name = forms.CharField(label="First Name", max_length=64)
        last_name = forms.CharField(label="Last Name", max_length=64)
        phone = forms.CharField(label="Phone #")
        address = AddressField(label="Address")
        credit_card = CreditCardField(label="Credit Card")

    form_data = {
        "first_name": "TestFirstName",
        "last_name": "TestLastName",
        "phone": "555-555-5555",
        "address_0": "123 Main St.", # Street
        "address_1": "Houston", # City
        "address_2": "Texas", # State
        "address_3": "77065", # Zip
        "address_4": "US", # Country (2 chars)
        "credit_card_0": "411111111111111", # Credit card number
        "credit_card_1": "1", # Expiration month
        "credit_card_2": "35", # Expiration year
        "credit_card_3": "444", # Credit card ccv code
    }
    form = MyCustomForm(form_data)

    print(f"{form.is_valid() = }") # True
    print(f"{type(form.clean()['address']) = }") # <authorizenet.apicontractsv1.customerAddressType>
    print(f"{type(form.clean()['credit_card']) = }") # <authorizenet.apicontractsv1.paymentType>
