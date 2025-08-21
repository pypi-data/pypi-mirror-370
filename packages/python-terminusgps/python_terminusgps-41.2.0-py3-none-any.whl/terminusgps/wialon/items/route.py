from terminusgps.wialon import flags
from terminusgps.wialon.items.base import WialonObject


class WialonRoute(WialonObject):
    """A Wialon `route <https://help.wialon.com/en/wialon-hosting/user-guide/monitoring-system/routes>`_."""

    def create(self, creator_id: str | int, name: str) -> dict[str, str]:
        """
        Creates the route in Wialon and sets its id.

        :param creator_id: A Wialon user id to set as the route's creator.
        :type creator_id: :py:obj:`int` | :py:obj:`str`
        :param name: Wialon route name.
        :type name: :py:obj:`str`
        :raises ValueError: If ``creator_id`` wasn't a digit.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A Wialon object dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise ValueError(f"'creator_id' must be a digit, got '{creator_id}'.")
        response = self.session.wialon_api.core_create_route(
            **{
                "creatorId": creator_id,
                "name": name,
                "dataFlags": flags.DataFlag.ROUTE_BASE,
            }
        )
        self.id = int(response.get("item", {}).get("id"))
        return response
