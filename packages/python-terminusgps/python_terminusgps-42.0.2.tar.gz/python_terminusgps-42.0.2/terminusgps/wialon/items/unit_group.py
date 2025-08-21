from collections.abc import Iterable

from terminusgps.wialon import flags
from terminusgps.wialon.items.base import WialonObject, requires_id


class WialonUnitGroup(WialonObject):
    """A Wialon `unit group <https://help.wialon.com/en/wialon-local/2504/user-guide/monitoring-system/units/unit-groups>`_."""

    def create(self, creator_id: int | str, name: str) -> dict[str, str]:
        """
        Creates the unit group in Wialon and sets its id.

        :param creator_id: A Wialon user id to set as the unit group's creator.
        :type creator_id: :py:obj:`int` | :py:obj:`str`
        :param name: Name for the unit group.
        :type name: :py:obj:`str`
        :raises ValueError: If ``creator_id`` wasn't a digit.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A Wialon object dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise ValueError(f"'creator_id' must be a digit, got '{creator_id}'.")
        response = self.session.wialon_api.core_create_unit_group(
            **{
                "creatorId": int(creator_id),
                "name": name,
                "dataFlags": flags.DataFlag.UNIT_BASE,
            }
        )
        self.id = int(response.get("item", {}).get("id"))
        return response

    @requires_id
    def update_units(self, unit_ids: Iterable[int]) -> dict[str, str]:
        """
        Sets the unit group's unit list in Wialon to ``unit_ids``.

        :param unit_ids: An iterable of Wialon unit id integers.
        :type unit_ids: :py:obj:`~typing.Iterable`[:py:obj:`int`]
        :raises AssertionError: If the Wialon unit group id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A dictionary containing the unit group's new unit list.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.unit_group_update_units(
            **{"itemId": self.id, "units": unit_ids}
        )
