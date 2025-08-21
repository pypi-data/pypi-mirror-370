import enum

ANET_XMLNS = "{AnetApi/xml/v1/schema/AnetApiSchema.xsd}"
"""Authorizenet XML namespace."""


class AuthorizenetSubscriptionStatus(enum.StrEnum):
    """Authorizenet subscription statuses."""

    ACTIVE = "active"
    """An active subscription."""
    EXPIRED = "expired"
    """An expired subscription."""
    SUSPENDED = "suspended"
    """A suspended subscription."""
    CANCELED = "canceled"
    """A canceled subscription."""
    TERMINATED = "terminated"
    """A terminated subscription."""
