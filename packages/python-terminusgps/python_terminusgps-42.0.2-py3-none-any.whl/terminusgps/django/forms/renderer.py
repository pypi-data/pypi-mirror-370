from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.forms.renderers import TemplatesSetting

if settings.configured and not hasattr(settings, "DEFAULT_FIELD_CLASS"):
    raise ImproperlyConfigured("'DEFAULT_FIELD_CLASS' setting is required.")


class TerminusgpsFormRenderer(TemplatesSetting):
    field_template_name = "terminusgps/field.html"
