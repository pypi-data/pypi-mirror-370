from abc import abstractmethod
from functools import wraps

from terminusgps.wialon import constants, flags
from terminusgps.wialon.session import WialonSession


def requires_id(meth):
    """Raises :py:exec:`AssertionError` before calling the method if the Wialon object's id wasn't set."""

    @wraps(meth)
    def wrapper(self, *args, **kwargs):
        assert self.id, "Wialon object id wasn't set."
        return meth(self, *args, **kwargs)

    return wrapper


class WialonObject:
    """Base class for Wialon objects in a Wialon session."""

    def __init__(self, session: WialonSession, id: int | str | None = None) -> None:
        """
        Sets the Wialon object's session and id.

        :param session: An active Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :param id: A Wialon object id. Default is :py:obj:`None`.
        :type id: :py:obj:`int` | :py:obj:`str` | :py:obj:`None`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if isinstance(id, str) and not id.isdigit():
            raise ValueError(f"'id' must be a digit, got '{id}'.")
        self._id = id
        self._session = session

    def __str__(self) -> str:
        """Returns the Wialon object id as a string."""
        return str(self.id)

    def __repr__(self) -> str:
        """Returns the Wialon object type and parameters used to initialize it."""
        return f"{type(self).__name__}(id={self.id}, session={self.session.id})"

    @property
    def session(self) -> WialonSession:
        """Wialon object API session."""
        return self._session

    @property
    def id(self) -> int | None:
        """Wialon object id."""
        return int(self._id) if self._id is not None else None

    @id.setter
    def id(self, other: int | str | None = None) -> None:
        """Sets :py:attr:`_id` to ``other``."""
        self._id = other

    @abstractmethod
    def create(self, *args, **kwargs) -> dict[str, str]:
        """Creates the object in Wialon and sets its id."""
        raise NotImplementedError("Subclasses must implement this method.")

    @requires_id
    def delete(self) -> dict[str, str]:
        """Deletes the object in Wialon."""
        return self.session.wialon_api.item_delete_item(**{"itemId": self.id})

    @requires_id
    def set_name(self, name: str) -> dict[str, str]:
        """Sets the object's name in Wialon."""
        return self.session.wialon_api.item_update_name(
            **{"itemId": self.id, "name": name}
        )

    @requires_id
    def get_name(self) -> str:
        """Gets and returns the object's name from Wialon."""
        return str(
            self.session.wialon_api.core_search_item(**{"id": self.id, "flags": 1})
            .get("item", {})
            .get("nm")
        )

    @requires_id
    def log_action(
        self, action: constants.WialonLogAction, new_value: str, old_value: str
    ) -> dict[str, str]:
        """Creates a log record for the Wialon object."""
        return self.session.wialon_api.item_add_log_record(
            **{
                "itemId": self.id,
                "action": str(action),
                "newValue": new_value,
                "oldValue": old_value,
            }
        )

    @requires_id
    def get_afields(self) -> list[dict[str, str]]:
        """
        Returns a list of admin field dictionaries from Wialon.

        :raises AssertionError: If the Wialon object id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A list of admin field dictionaries.
        :rtype: :py:obj:`list`[:py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]]

        """
        return list(
            self.session.wialon_api.core_search_item(
                **{"id": self.id, "flags": flags.DataFlag.UNIT_ADMIN_FIELDS}
            )
            .get("item", {})
            .get("aflds")
            .values()
        )

    @requires_id
    def set_afield(
        self, key: str, value: str, id: int | str | None = None
    ) -> dict[str, str]:
        """
        Sets an admin field in Wialon.

        If ``id`` isn't provided, a new admin field is created.

        :raises AssertionError: If the Wialon object id wasn't set.
        :raises ValueError: If ``id`` wasn't a digit.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: An admin field dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        if isinstance(id, str) and not id.isdigit():
            raise ValueError(f"'id' must be a digit, got '{id}'.")
        return self.session.wialon_api.item_update_admin_field(
            **{
                "itemId": self.id,
                "id": int(id) if id else 0,
                "callMode": "update" if id else "create",
                "n": key,
                "v": value,
            }
        )

    @requires_id
    def delete_afield(self, id: int | str) -> dict[str, str]:
        """
        Deletes an admin field by id in Wialon.

        :raises AssertionError: If the Wialon object id wasn't set.
        :raises ValueError: If ``id`` wasn't a digit.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: An empty dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        if isinstance(id, str) and not id.isdigit():
            raise ValueError(f"'id' must be a digit, got '{id}'.")
        return self.session.wialon_api.item_update_admin_field(
            **{"itemId": self.id, "id": int(id), "callMode": "delete"}
        )

    @requires_id
    def get_cfields(self) -> list[dict[str, str]]:
        """
        Returns a list of custom field dictionaries from Wialon.

        :raises AssertionError: If the Wialon object id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A list of admin field dictionaries.
        :rtype: :py:obj:`list`[:py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]]

        """
        return list(
            self.session.wialon_api.core_search_item(
                **{"id": self.id, "flags": flags.DataFlag.UNIT_CUSTOM_FIELDS}
            )
            .get("item", {})
            .get("flds")
            .values()
        )

    @requires_id
    def set_cfield(
        self, key: str, value: str, id: int | str | None = None
    ) -> dict[str, str]:
        """
        Sets a custom field in Wialon.

        If ``id`` isn't provided, a new custom field is created.

        :raises AssertionError: If the Wialon object id wasn't set.
        :raises ValueError: If ``id`` wasn't a digit.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A custom field dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        if isinstance(id, str) and not id.isdigit():
            raise ValueError(f"'id' must be a digit, got '{id}'.")
        return self.session.wialon_api.item_update_custom_field(
            **{
                "itemId": self.id,
                "id": int(id) if id else 0,
                "callMode": "update" if id else "create",
                "n": key,
                "v": value,
            }
        )

    @requires_id
    def delete_cfield(self, id: int | str) -> dict[str, str]:
        """
        Deletes a custom field by id in Wialon.

        :raises AssertionError: If the Wialon object id wasn't set.
        :raises ValueError: If ``id`` wasn't a digit.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: An empty dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        if isinstance(id, str) and not id.isdigit():
            raise ValueError(f"'id' must be a digit, got '{id}'.")
        return self.session.wialon_api.item_update_custom_field(
            **{"itemId": self.id, "id": int(id), "callMode": "delete"}
        )

    @requires_id
    def set_pfield(self, key: str, value: str) -> dict[str, str]:
        """
        Sets a profile field for the object in Wialon.

        :raises AssertionError: If the Wialon object id wasn't set.
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A profile field dictionary.
        :rtype: :py:obj:`dict`[:py:obj:`str`, :py:obj:`str`]

        """
        return self.session.wialon_api.item_update_profile_field(
            **{"itemId": self.id, "n": key, "v": value}
        )
