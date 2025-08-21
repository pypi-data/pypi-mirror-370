from collections.abc import Iterable

from terminusgps.wialon import flags
from terminusgps.wialon.items.base import WialonObject, requires_id


class WialonUnit(WialonObject):
    """A Wialon `unit <https://help.wialon.com/en/wialon-hosting/user-guide/management-system/units>`_."""

    def create(
        self, creator_id: int | str, name: str, hw_type_id: int | str
    ) -> dict[str, str]:
        """
        Creates the unit in Wialon and sets its id.

        :param creator_id: A Wialon user id to set as the unit's creator.
        :type creator_id: :py:obj:`int` | :py:obj:`str`
        :param name: Wialon unit name.
        :type name: :py:obj:`str`
        :param hw_type_id: A Wialon hardware type id.
        :type hw_type_id: :py:obj:`int` | :py:obj:`str`
        :raises ValueError: If ``creator_id`` wasn't a digit.
        :raises ValueError: If ``hw_type_id`` wasn't a digit.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A Wialon object dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise ValueError(f"'creator_id' must be a digit, got '{creator_id}'.")
        if isinstance(hw_type_id, str) and not hw_type_id.isdigit():
            raise ValueError(f"'hw_type_id' must be a digit, got '{hw_type_id}'.")
        response = self.session.wialon_api.core_create_unit(
            **{
                "creatorId": int(creator_id),
                "name": name,
                "hwTypeId": int(hw_type_id),
                "dataFlags": flags.DataFlag.UNIT_BASE,
            }
        )
        self.id = int(response.get("item", {}).get("id"))
        return response

    @requires_id
    def activate(self) -> dict[str, str]:
        """
        Activates the unit in Wialon.

        :raises AssertionError: If the Wialon unit id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A dictionary with the unit's current status.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.unit_set_active(
            **{"itemId": self.id, "active": 1}
        )

    @requires_id
    def deactivate(self) -> dict[str, str]:
        """
        Deactivates the unit in Wialon.

        :raises AssertionError: If the Wialon unit id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A dictionary with the unit's current status.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.unit_set_active(
            **{"itemId": self.id, "active": 0}
        )

    @requires_id
    def execute_command(
        self,
        command_name: str,
        link_type: str = "vrt",
        parameters: str = "",
        timeout: int = 300,
        flags: int = 0,
    ) -> dict[str, str]:
        """
        Executes a unit command in Wialon.

        :param command_name: Name of the command.
        :type command_name: :py:obj:`str`
        :param link_type: Link type to send the command with. Default is ``"vrt"``.
        :type link_type: :py:obj:`str`
        :param parameters: Additional command execution parameters. Default is ``""``.
        :type parameters: :py:obj:`str`
        :param timeout: How long (in seconds) before timing out the command execution. Default is ``300``.
        :type timeout: :py:obj:`int`
        :param flags: Command execution flags. Default is ``0``.
        :type flags: :py:obj:`int`
        :raises AssertionError: If the Wialon unit id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: An empty dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.unit_exec_cmd(
            **{
                "itemId": self.id,
                "commandName": command_name,
                "linkType": link_type,
                "param": parameters,
                "timeout": timeout,
                "flags": flags,
            }
        )

    @requires_id
    def get_command_definitions(
        self, command_ids: Iterable[int] | None = None
    ) -> dict[str, str]:
        """
        Returns the unit's command definition data by id(s).

        Returns *all* command definition data if ``command_ids`` is :py:obj:`None`.

        :param command_ids: An iterable of command id integers. Default is :py:obj:`None`.
        :type command_ids: :py:obj:`~collections.abc.Iterable`[:py:obj:`int`] | :py:obj:`None`
        :raises AssertionError: If the Wialon unit id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A dictionary of command definition data.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.unit_get_command_definition_data(
            **{"itemId": self.id, "col": command_ids}
            if command_ids is not None
            else {"itemId": self.id}
        )

    @requires_id
    def get_imei(self) -> str:
        return str(
            self.session.wialon_api.core_search_item(
                **{"id": self.id, "flags": flags.DataFlag.UNIT_ADVANCED_PROPERTIES}
            )
            .get("item", {})
            .get("uid")
        )
