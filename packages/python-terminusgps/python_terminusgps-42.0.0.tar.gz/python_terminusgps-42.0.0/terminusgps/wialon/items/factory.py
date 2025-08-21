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

    def create(self, items_type: str, *args, **kwargs) -> WialonObject:
        """Creates a Wialon object in Wialon and returns its Python equivalent."""
        cls = self._get_wialon_cls(items_type)
        if cls is None:
            raise ValueError(f"Invalid Wialon items type: '{items_type}'.")
        return self._create_wialon_obj(cls, *args, **kwargs)

    def get(self, items_type: str, id: int | str) -> WialonObject:
        """Retrieves a Wialon object from Wialon and returns its Python equivalent."""
        cls = self._get_wialon_cls(items_type)
        if cls is None:
            raise ValueError(f"Invalid Wialon items type: '{items_type}'.")
        return self._retrieve_wialon_obj(cls, id)

    def _get_wialon_cls(self, items_type) -> WialonObject | None:
        return WIALON_ITEMSTYPE_MAP.get(items_type)

    def _create_wialon_obj(self, cls, *args, **kwargs) -> WialonObject:
        obj = cls(session=self.session, id=None)
        obj.create(*args, **kwargs)
        return obj

    def _retrieve_wialon_obj(self, cls, id) -> WialonObject:
        return cls(session=self.session, id=int(id))
