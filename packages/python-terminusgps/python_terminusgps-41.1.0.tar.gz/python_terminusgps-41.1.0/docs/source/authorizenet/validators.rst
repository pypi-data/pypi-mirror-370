Validators
==========

.. automodule:: terminusgps.authorizenet.validators
   :members:

=====
Usage
=====

.. code:: python

    from django import forms

    from terminusgps.authorizenet.validators import (
        validate_credit_card_number,
        validate_credit_card_expiry_month,
        validate_credit_card_expiry_year,
    )

    class CreditCardForm(forms.Form):
        # Adding the validators to a form field renders error messages properly
        cc_number = forms.CharField(
            max_length=17, validators=[validate_credit_card_number]
        )
        cc_expiry_month = forms.CharField(
            max_length=2, validators=[validate_credit_card_expiry_month]
        )
        cc_expiry_year = forms.CharField(
            max_length=2, validators=[validate_credit_card_expiry_year]
        )
