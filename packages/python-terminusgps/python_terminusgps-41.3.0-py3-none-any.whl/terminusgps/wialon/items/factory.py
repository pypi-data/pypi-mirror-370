from terminusgps.wialon.items.account import WialonAccount
from terminusgps.wialon.items.base import WialonObject
from terminusgps.wialon.items.resource import WialonResource
from terminusgps.wialon.items.retranslator import WialonRetranslator
from terminusgps.wialon.items.route import WialonRoute
from terminusgps.wialon.items.unit import WialonUnit
from terminusgps.wialon.items.unit_group import WialonUnitGroup
from terminusgps.wialon.items.user import WialonUser
from terminusgps.wialon.session import WialonSession

WIALON_ITEMSTYPE_MAP = {
    "account": WialonAccount,
    "avl_hw": None,
    "avl_resource": WialonResource,
    "avl_retranslator": WialonRetranslator,
    "avl_route": WialonRoute,
    "avl_unit": WialonUnit,
    "avl_unit_group": WialonUnitGroup,
    "user": WialonUser,
}


class WialonObjectFactory:
    """Creates and retrieves Wialon objects from Wialon."""

    def __init__(self, session: WialonSession) -> None:
        # TODO: Add session refreshing
        self.session = session

    def get(self, id: int | str, items_type: str) -> WialonObject:
        """Returns a Wialon object that already exists in Wialon by id."""
        if isinstance(id, str) and not id.isdigit():
            raise ValueError(f"'id' can only be digits, got '{id}'.")
        if items_type not in WIALON_ITEMSTYPE_MAP:
            raise ValueError(f"Invalid Wialon items type: '{items_type}'.")
        cls = WIALON_ITEMSTYPE_MAP.get(items_type)
        if cls is None:
            raise ValueError(f"Wialon items type '{items_type}' is not implemented.")
        return cls(session=self.session, id=int(id))

    def create(self, items_type: str, *args, **kwargs) -> WialonObject:
        """Returns a Wialon object after creating it in Wialon."""
        if items_type not in WIALON_ITEMSTYPE_MAP:
            raise ValueError(f"Invalid Wialon items type: '{items_type}'.")
        cls = WIALON_ITEMSTYPE_MAP.get(items_type)
        if cls is None:
            raise ValueError(f"Wialon items type '{items_type}' is not implemented.")
        obj = cls(session=self.session, id=None)
        obj.create(*args, **kwargs)
        return obj
