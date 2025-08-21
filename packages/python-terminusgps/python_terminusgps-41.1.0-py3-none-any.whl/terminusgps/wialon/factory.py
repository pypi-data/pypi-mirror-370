from terminusgps.wialon.items import (
    WialonResource,
    WialonRetranslator,
    WialonRoute,
    WialonUnit,
    WialonUnitGroup,
    WialonUser,
)
from terminusgps.wialon.items.base import WialonObject
from terminusgps.wialon.session import WialonSession

WIALON_ITEM_MAP = {
    "avl_hw": None,
    "avl_resource": WialonResource,
    "avl_retranslator": WialonRetranslator,
    "avl_unit": WialonUnit,
    "avl_unit_group": WialonUnitGroup,
    "user": WialonUser,
    "avl_route": WialonRoute,
}


class WialonObjectCreationError(Exception):
    """Raised when a factory fails to create a Wialon object."""


def create_wialon_object(
    session: WialonSession, items_type: str, *args, **kwargs
) -> WialonObject:
    """
    Creates an ``items_type`` object in Wialon and returns it as a Python object.

    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :param items_type: A Wialon items type string.
    :type items_type: :py:obj:`str`
    :param args: Positional arguments to pass to the Wialon object's :py:meth:`create` method.
    :param kwargs: Keyword arguments to pass to the Wialon object's :py:meth:`create` method.
    :raises WialonAPIError: If something went wrong calling the Wialon API.
    :raises WialonObjectCreationError: If something went wrong creating the object in Wialon.
    :returns: A Wialon object.
    :rtype: :py:obj:`~terminusgps.wialon.items.base.WialonObject`

    """
    if items_type not in WIALON_ITEM_MAP:
        raise ValueError(f"Unknown Wialon items type: '{items_type}'.")

    cls = WIALON_ITEM_MAP.get(items_type)
    if cls is None:
        raise ValueError(f"Wialon items type '{items_type}' is not implemented.")

    obj = cls(session)
    obj.create(*args, **kwargs)
    if not obj.id:
        raise WialonObjectCreationError(
            f"Failed to execute create({args = }, {kwargs = }) on '{obj}'."
        )
    return obj
