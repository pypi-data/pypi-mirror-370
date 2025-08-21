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
        """
        Returns a Wialon object that already exists in Wialon by id.

        :param id: A Wialon object id.
        :type id: :py:obj:`int` | :py:obj:`str`
        :param items_type: A Wialon items type string.
        :type items_type: :py:obj:`str`
        :raises ValueError: If ``id`` wasn't a digit.
        :raises ValueError: If ``items_type`` was invalid.
        :returns: An existing Wialon object.
        :rtype: :py:obj:`WialonObject`

        Available items_type options:

        +-------------------------+---------------------------------------------------------------------+
        | key                     | class                                                               |
        +=========================+=====================================================================+
        | ``"account"``           | :py:obj:`~terminusgps.wialon.items.account.WialonAccount`           |
        +-------------------------+---------------------------------------------------------------------+
        | ``"avl_resource"``      | :py:obj:`~terminusgps.wialon.items.resource.WialonResource`         |
        +-------------------------+---------------------------------------------------------------------+
        | ``"avl_retranslator"``  | :py:obj:`~terminusgps.wialon.items.retranslator.WialonRetranslator` |
        +-------------------------+---------------------------------------------------------------------+
        | ``"avl_route"``         | :py:obj:`~terminusgps.wialon.items.route.WialonRoute`               |
        +-------------------------+---------------------------------------------------------------------+
        | ``"avl_unit"``          | :py:obj:`~terminusgps.wialon.items.unit.WialonUnit`                 |
        +-------------------------+---------------------------------------------------------------------+
        | ``"avl_unit_group"``    | :py:obj:`~terminusgps.wialon.items.unit_group.WialonUnitGroup`      |
        +-------------------------+---------------------------------------------------------------------+
        | ``"user"``              | :py:obj:`~terminusgps.wialon.items.user.WialonUser`                 |
        +-------------------------+---------------------------------------------------------------------+

        """
        if isinstance(id, str) and not id.isdigit():
            raise ValueError(f"'id' can only be digits, got '{id}'.")
        if items_type not in WIALON_ITEMSTYPE_MAP:
            raise ValueError(f"Invalid Wialon items type: '{items_type}'.")
        cls = WIALON_ITEMSTYPE_MAP.get(items_type)
        if cls is None:
            raise ValueError(f"Wialon items type '{items_type}' is not implemented.")
        return cls(session=self.session, id=int(id))

    def create(self, items_type: str, *args, **kwargs) -> WialonObject:
        """
        Returns a Wialon object after creating it in Wialon.

        :param items_type: A Wialon items type string.
        :type items_type: :py:obj:`str`
        :param args: Positional arguments passed to the object's :py:meth:`create` method.
        :param kwargs: Keyword arguments passed to the object's :py:meth:`create` method.
        :raises ValueError: If ``items_type`` was invalid.
        :returns: A newly created Wialon object.
        :rtype: :py:obj:`WialonObject`

        Available items_type options:

        +-------------------------+---------------------------------------------------------------------+
        | key                     | class                                                               |
        +=========================+=====================================================================+
        | ``"account"``           | :py:obj:`~terminusgps.wialon.items.account.WialonAccount`           |
        +-------------------------+---------------------------------------------------------------------+
        | ``"avl_resource"``      | :py:obj:`~terminusgps.wialon.items.resource.WialonResource`         |
        +-------------------------+---------------------------------------------------------------------+
        | ``"avl_retranslator"``  | :py:obj:`~terminusgps.wialon.items.retranslator.WialonRetranslator` |
        +-------------------------+---------------------------------------------------------------------+
        | ``"avl_route"``         | :py:obj:`~terminusgps.wialon.items.route.WialonRoute`               |
        +-------------------------+---------------------------------------------------------------------+
        | ``"avl_unit"``          | :py:obj:`~terminusgps.wialon.items.unit.WialonUnit`                 |
        +-------------------------+---------------------------------------------------------------------+
        | ``"avl_unit_group"``    | :py:obj:`~terminusgps.wialon.items.unit_group.WialonUnitGroup`      |
        +-------------------------+---------------------------------------------------------------------+
        | ``"user"``              | :py:obj:`~terminusgps.wialon.items.user.WialonUser`                 |
        +-------------------------+---------------------------------------------------------------------+

        """
        if items_type not in WIALON_ITEMSTYPE_MAP:
            raise ValueError(f"Invalid Wialon items type: '{items_type}'.")
        cls = WIALON_ITEMSTYPE_MAP.get(items_type)
        if cls is None:
            raise ValueError(f"Wialon items type '{items_type}' is not implemented.")
        obj = cls(session=self.session, id=None)
        obj.create(*args, **kwargs)
        return obj
