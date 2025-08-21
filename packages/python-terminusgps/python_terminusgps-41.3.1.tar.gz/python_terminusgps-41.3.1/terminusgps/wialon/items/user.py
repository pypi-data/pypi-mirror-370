from terminusgps.wialon import flags
from terminusgps.wialon.items.base import WialonObject, requires_id


class WialonUser(WialonObject):
    """A Wialon `user <https://help.wialon.com/en/wialon-hosting/user-guide/management-system/users>`_."""

    def create(self, creator_id: int | str, name: str, password: str) -> dict[str, str]:
        """
        Creates the user in Wialon and sets its id.

        :param creator_id: A Wialon user id to set as the new user's creator.
        :type creator_id: :py:obj:`int` | :py:obj:`str`
        :param name: Wialon user name.
        :type name: :py:obj:`str`
        :param password: Wialon user password.
        :type password: :py:obj:`str`
        :raises ValueError: If ``creator_id`` wasn't a digit.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A Wialon object dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise ValueError(f"'creator_id' must be a digit, got '{creator_id}'.")
        response = self.session.wialon_api.core_create_user(
            **{
                "creatorId": int(creator_id),
                "name": name,
                "password": password,
                "dataFlags": flags.DataFlag.USER_BASE,
            }
        )
        self.id = int(response.get("item", {}).get("id"))
        return response

    @requires_id
    def get_access(
        self, object_type: str, direct: bool = True, flags: int = 0x1
    ) -> dict[str, str]:
        """
        Returns a dictionary of Wialon objects the user has access to.

        :param object_type: A Wialon object type.
        :type object_type: :py:obj:`str`
        :param direct: Whether or not to exclude objects the user doesn't have direct access to. Default is :py:obj:`True`.
        :type direct: :py:obj:`bool`
        :param flags: Response flags. Default is ``0x1``.
        :type flags: :py:obj:`int`
        :raises AssertionError: If the Wialon user id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A dictionary of Wialon objects.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.user_get_items_access(
            **{
                "userId": self.id,
                "directAccess": int(direct),
                "itemSuperclass": object_type,
                "flags": flags,
            }
        )

    @requires_id
    def set_access(self, obj: WialonObject, access_mask: int) -> dict[str, str]:
        """
        Sets the user's access to ``obj`` according to ``access_mask`` in Wialon.

        :param object_id: A Wialon object id.
        :type object_id: :py:obj:`int`
        :param access_mask: A Wialon access mask integer.
        :type access_mask: :py:obj:`int`
        :raises AssertionError: If the Wialon user id wasn't set.
        :raises ValueError: If the other Wialon object's id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: An empty dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        if obj.id is None:
            raise ValueError("Other Wialon object's id wasn't set.")
        return self.session.wialon_api.user_update_item_access(
            **{"userId": self.id, "itemId": obj.id, "accessMask": access_mask}
        )

    @requires_id
    def set_flags(self, flags: int, flags_mask: int) -> dict[str, str]:
        """
        Sets the user settings flags in Wialon.

        :param flags: A Wialon user settings flag integer.
        :type flags: :py:obj:`int`
        :param flags_mask: An integer mask which determines which bits will be changed.
        :type flags_mask: :py:obj:`int`
        :raises AssertionError: If the Wialon user id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A dictionary containing the user's new settings flags.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.user_update_user_flags(
            **{"userId": self.id, "flags": flags, "flagsMask": flags_mask}
        )

    @requires_id
    def set_password(self, old_password: str, new_password: str) -> dict[str, str]:
        """
        Sets the user's password to ``new_password`` in Wialon.

        :param old_password: The user's old Wialon password.
        :type old_password: :py:obj:`str`
        :param new_password: The user's new Wialon password.
        :type new_password: :py:obj:`str`
        :raises AssertionError: If the Wialon user id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: An empty dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.user_update_password(
            **{
                "userId": self.id,
                "oldPassword": old_password,
                "newPassword": new_password,
            }
        )
