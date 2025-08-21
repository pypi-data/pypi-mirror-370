Mixins
======

.. autoclass:: terminusgps.django.mixins.HtmxTemplateResponseMixin
   :members:
   :autoclasstoc:

=====
Usage
=====

.. code:: python

    # views.py
    from django.views.generic import TemplateView
    from terminusgps.django.mixins import HtmxTemplateResponseMixin

    # The mixin **MUST** be inherited before a Django view, otherwise the view's MRO will break.
    class HtmxTemplateView(HtmxTemplateResponseMixin, TemplateView):
        content_type = "text/html"
        template_name = "htmx.html"
        partial_template_name = "partials/_htmx.html" # Rendered if htmx request is made.

Common practice is to include the partial template in the main template:

.. code:: html

    <!-- templates/htmx.html -->
    {% extends "layout.html" %}
    {% block content %}
    {% include "partials/_htmx.html" %}
    {% endblock content %}
