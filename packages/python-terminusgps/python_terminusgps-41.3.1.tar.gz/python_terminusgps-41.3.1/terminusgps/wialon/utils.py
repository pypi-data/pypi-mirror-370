import secrets
import string
import typing

from terminusgps.wialon import flags
from terminusgps.wialon.items.unit import WialonUnit
from terminusgps.wialon.items.user import WialonUser
from terminusgps.wialon.session import WialonSession


def get_hw_types(session: WialonSession) -> list[dict[str, str | int]]:
    """
    Returns a list of hardware type objects for Wialon.

    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :returns: A list of hardware types.
    :rtype: :py:obj:`list`

    Hardware type format:

    +----------+--------------------+
    | key      | value              |
    +==========+====================+
    | ``id``   | Hardware type id   |
    +----------+--------------------+
    | ``name`` | Hardware type name |
    +----------+--------------------+

    """
    return session.wialon_api.core_get_hw_types()


def get_user_by_name(name: str, session: WialonSession) -> WialonUser | None:
    """
    Returns a Wialon user by name, if it exists.

    :param name: A Wialon user name.
    :type name: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :returns: A Wialon unit, if any.
    :rtype: :py:obj:`~terminusgps.wialon.items.unit.WialonUnit` | :py:obj:`None`

    """
    response = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "user",
                "propName": "sys_name",
                "propValueMask": name,
                "sortType": "sys_name",
                "propType": "property",
            },
            "force": 0,
            "flags": flags.DataFlag.USER_BASE,
            "from": 0,
            "to": 0,
        }
    )
    if int(response.get("totalItemsCount")) == 1:
        if user_id := int(response.get("items")[0].get("id")):
            return WialonUser(session, user_id)


def get_carrier_names(session: WialonSession) -> list[str]:
    """
    Returns a list of all telecommunication carrier company names present in Wialon.

    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :returns: A list of telecommunication carrier company names.
    :rtype: :py:obj:`list`

    """
    response = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": "rel_adminfield_name,rel_adminfield_value",
                "propValueMask": "carrier,*",
                "sortType": "sys_id,sys_id",
                "propType": "property",
            },
            "force": 0,
            "flags": flags.DataFlag.UNIT_BASE + flags.DataFlag.UNIT_ADMIN_FIELDS,
            "from": 0,
            "to": 0,
        }
    )
    carrier_names: list[str] = [
        field["v"]
        for item in response.get("items", [{}])
        for field in item.get("aflds", {}).values()
        if field["n"] == "carrier" and field["v"]
    ]
    return sorted(list(frozenset(carrier_names)))


def get_units_by_carrier(
    carrier_name: str, session: WialonSession
) -> list[WialonUnit] | None:
    """
    Returns a list of all units by telecommunications carrier company name.

    :param carrier_name: A telecommunications carrier company name, e.g. ``"US Cell"`` or ``"Conetixx"``.
    :type carrier_name: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :returns: A list of units, if any were found.
    :rtype: :py:obj:`list`

    """
    response = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": "rel_adminfield_name",
                "propValueMask": f"carrier:{carrier_name}",
                "sortType": "rel_adminfield_name",
                "propType": "property",
            },
            "force": 0,
            "flags": flags.DataFlag.UNIT_BASE,
            "from": 0,
            "to": 0,
        }
    )
    if units := response.get("items", []):
        return [WialonUnit(session=session, id=int(unit.get("id"))) for unit in units]


def get_unit_by_iccid(iccid: str, session: WialonSession) -> WialonUnit | None:
    """
    Returns a unit by iccid (SIM card #).

    :param iccid: A SIM card #.
    :type iccid: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :returns: The unit, if it was found.
    :rtype: :py:obj:`~terminusgps.wialon.items.WialonUnit` | :py:obj:`None`

    """
    response = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": "rel_adminfield_name",
                "propValueMask": f"iccid:{iccid}",
                "sortType": "rel_adminfield_name",
                "propType": "property",
            },
            "force": 0,
            "flags": flags.DataFlag.UNIT_BASE,
            "from": 0,
            "to": 0,
        }
    )
    if int(response.get("totalItemsCount", 0)) == 1:
        if unit_id := int(response.get("items")[0].get("id")):
            return WialonUnit(session, unit_id)


def get_unit_by_imei(imei: int | str, session: WialonSession) -> WialonUnit | None:
    """
    Takes a Wialon unit's IMEI # and returns its unit id.

    :param imei: A Wialon unit's IMEI #.
    :type imei: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :raises ValueError: If ``imei`` wasn't a digit.
    :raises WialonAPIError: If something went wrong calling the Wialon API.
    :returns: A Wialon unit, if it was found.
    :rtype: :py:obj:`str` | :py:obj:`None`

    """
    if isinstance(imei, str) and not imei.isdigit():
        raise ValueError(f"'imei' must be a digit, got '{imei}'.")
    response = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_unique_id",
                "propValueMask": imei,
                "sortType": "sys_unique_id",
                "propType": "property",
            },
            "force": 0,
            "flags": flags.DataFlag.UNIT_BASE,
            "from": 0,
            "to": 0,
        }
    )
    if int(response.get("totalItemsCount", 0)) == 1:
        if unit_id := response.get("items")[0].get("id"):
            return WialonUnit(session, unit_id)


def get_vin_info(vin_number: str, session: WialonSession) -> dict[str, typing.Any]:
    """
    Retrieves vehicle data from a VIN number.

    :param value: A vehicle's VIN number.
    :type value: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :returns: A dictionary of vehicle information, if any was found.
    :rtype: :py:obj:`dict`

    """
    response = session.wialon_api.unit_get_vin_info(**{"vin": vin_number})
    results = response.get("vin_lookup_result", {})
    if "error" in results.keys():
        return {}
    return {field.get("n"): field.get("v") for field in results.get("pflds")}


def check_unique(object_type: str, name: str, session: WialonSession) -> bool:
    return bool(
        session.wialon_api.core_check_unique(
            **{"type": object_type, "value": name}
        ).get("result")
    )


def generate_wialon_password(length: int = 32) -> str:
    """
    Generates a Wialon compliant password between ``8`` and ``64`` characters.

    The generated password will contain:

        - At least one uppercase letter.
        - At least one lowercase letter.
        - At least one special symbol.
        - At least three digits.

    :param length: Length of the generated password. Default is :py:obj:`32`.
    :type length: :py:obj:`int`
    :raises ValueError: If ``length`` is less than ``8`` or greater than ``64``.
    :returns: A Wialon compliant password.
    :rtype: :py:obj:`str`

    """
    min_length, max_length = 8, 64
    if length > max_length:
        raise ValueError(
            f"Password cannot be greater than {max_length} characters in length, got {length}."
        )
    elif length < min_length:
        raise ValueError(
            f"Password cannot be less than {min_length} characters in length, got {length}."
        )

    s0 = list(string.ascii_uppercase)
    s1 = list(string.ascii_lowercase)
    s2 = list(string.digits)
    s3 = list("!@#$%^*()[]-_+")

    while True:
        password = "".join([secrets.choice(s0 + s1 + s2 + s3) for _ in range(length)])
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3
            and any(c in s3 for c in password)
        ):
            break
    return password
