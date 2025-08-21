from typing import TypedDict

from terminusgps.wialon import flags
from terminusgps.wialon.items.base import WialonObject

WialonRetranslatorConfiguration = TypedDict(
    "WialonRetranslatorConfiguration",
    {
        "protocol": str,
        "server": str,
        "port": int,
        "auth": str,
        "ssl": int,
        "debug": int,
        "v6type": int,
    },
)


class WialonRetranslator(WialonObject):
    """A Wialon `retranslator <https://wialon.com/en/gps-hardware/soft>`_."""

    def create(
        self, creator_id: int | str, name: str, config: WialonRetranslatorConfiguration
    ) -> dict[str, str]:
        """
        Creates the retranslator in Wialon and sets its id.

        :param creator_id: A Wialon user id to set as the retranslator's creator.
        :type creator_id: :py:obj:`int` | :py:obj:`str`
        :param name: Wialon retranslator name.
        :type name: :py:obj:`str`
        :param config: Wialon retranslator configuration.
        :type config: :py:obj:`~terminusgps.wialon.items.retranslator.WialonRetranslatorConfiguration`
        :raises ValueError: If ``creator_id`` wasn't a digit.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A Wialon object dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise ValueError(f"'creator_id' must be a digit, got '{creator_id}'.")
        response = self.session.wialon_api.core_create_retranslator(
            **{
                "creatorId": int(creator_id),
                "name": name,
                "config": config,
                "dataFlags": flags.DataFlag.UNIT_BASE,
            }
        )
        self.id = int(response.get("item", {}).get("id"))
        return response
