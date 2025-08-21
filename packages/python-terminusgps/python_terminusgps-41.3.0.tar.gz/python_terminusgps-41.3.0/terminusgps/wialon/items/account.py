from collections.abc import Iterable
from decimal import Decimal
from typing import override

from terminusgps.wialon.items.base import WialonObject, requires_id


class WialonAccount(WialonObject):
    """A Wialon `account <https://help.wialon.com/en/wialon-hosting/user-guide/management-system/accounts-and-resources>`_."""

    def create(self, resource_id: int | str, billing_plan: str) -> dict[str, str]:
        """
        Creates the account in Wialon and sets its id.

        :param resource_id: A Wialon resource id.
        :type creator_id: :py:obj:`int` | :py:obj:`str`
        :param billing_plan: A Wialon account billing plan.
        :type billing_plan: :py:obj:`str`
        :raises ValueError: If ``resource_id`` wasn't a digit.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A Wialon object dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        if isinstance(resource_id, str) and not resource_id.isdigit():
            raise ValueError(f"'resource_id' must be a digit, got '{resource_id}'.")
        response = self.session.wialon_api.account_create_account(
            **{"itemId": resource_id, "plan": billing_plan}
        )
        self.id = resource_id
        return response

    @override
    @requires_id
    def delete(self, reasons: Iterable[str] | None = None) -> dict[str, str]:
        """
        Deletes the account in Wialon.

        :param reasons: An iterable of reason strings.
        :type reasons: :py:obj:`~collections.abc.Iterable`[:py:obj:`str`]
        :raises AssertionError: If the Wialon account id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: An empty dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.account_delete_account(
            **{"itemId": self.id, "reasons": reasons}
            if reasons is not None
            else {"itemId": self.id}
        )

    @requires_id
    def activate(self) -> dict[str, str]:
        """
        Enables the account in Wialon.

        :raises AssertionError: If the Wialon account id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: An empty dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.account_enable_account(
            **{"itemId": self.id, "enable": 1}
        )

    @requires_id
    def deactivate(self) -> dict[str, str]:
        """
        Disables the account in Wialon.

        :raises AssertionError: If the Wialon account id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: An empty dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.account_enable_account(
            **{"itemId": self.id, "enable": 0}
        )

    @requires_id
    def do_payment(
        self, balance_update: Decimal, days_update: int, description: str
    ) -> dict[str, str]:
        """
        Makes an account payment in Wialon.

        :param balance_update: Amount to update the account balance by. Can be negative.
        :type balance_update: :py:obj:`~decimal.Decimal`
        :param days_update: Amount of days to add to the account.
        :type days_update: :py:obj:`int`
        :param description: A description for the payment.
        :type description: :py:obj:`str`
        :raises AssertionError: If the Wialon account id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: An empty dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.account_do_payment(
            **{
                "itemId": self.id,
                "balanceUpdate": str(balance_update),
                "daysUpdate": days_update,
                "description": description,
            }
        )

    @requires_id
    def set_dealer_rights(self, enabled: bool) -> dict[str, str]:
        """
        Enables or disables the account's dealer rights in Wialon.

        :param enabled: Whether to set the account as a dealer or not.
        :type enabled: :py:obj:`bool`
        :raises AssertionError: If the Wialon account id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: An empty dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.account_update_dealer_rights(
            **{"itemId": self.id, "enable": int(enabled)}
        )

    @requires_id
    def set_flags(
        self,
        flags: int,
        block_balance: Decimal = Decimal("0.00"),
        deny_balance: Decimal = Decimal("0.00"),
    ) -> dict[str, str]:
        """
        Sets settings flags for the account in Wialon.

        :param flags: A Wialon account settings flag integer.
        :type flags: :py:obj:`int`
        :param block_balance: Balance required for account blocking. Default is ``"0.00"``.
        :type block_balance: :py:obj:`~decimal.Decimal`
        :param deny_balance: Balance required for service denial. Default is ``"0.00"``.
        :type deny_balance: :py:obj:`~decimal.Decimal`
        :raises AssertionError: If the Wialon account id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: An empty dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.account_update_flags(
            **{
                "itemId": self.id,
                "flags": flags,
                "blockBalance": block_balance,
                "denyBalance": deny_balance,
            }
        )

    @requires_id
    def set_plan(self, name: str) -> dict[str, str]:
        """
        Sets the account's billing plan to ``name``.

        :param name: A Wialon billing plan name.
        :type name: :py:obj:`str`
        :raises AssertionError: If the Wialon account id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: An empty dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.account_update_plan(
            **{"itemId": self.id, "plan": name}
        )

    @requires_id
    def set_minimum_days(self, days: int) -> dict[str, str]:
        """
        Sets the account's minimum days to ``days`` in Wialon.

        :param days: Minimum number of days as an integer.
        :type days: :py:obj:`int`
        :raises AssertionError: If the Wialon account id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: An empty dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.account_update_min_days(
            **{"itemId": self.id, "minDays": days}
        )

    @requires_id
    def get_data(self, response_type: int = 1) -> dict[str, str]:
        """
        Returns account data from Wialon.

        :param response_type: A response flag integer. Default is ``1``.
        :type response_type: :py:obj:`int`
        :raises AssertionError: If the Wialon account id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A dictionary containing the account's data from Wialon.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.account_get_account_data(
            **{"itemId": self.id, "type": response_type}
        )
