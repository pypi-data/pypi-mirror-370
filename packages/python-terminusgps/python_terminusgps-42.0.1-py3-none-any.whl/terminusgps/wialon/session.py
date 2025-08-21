import os
import typing

import wialon.api


class WialonAPIError(Exception):
    def __init__(self, message, *args, **kwargs) -> None:
        self.message = message
        self._code = int(message._code)
        super().__init__(message, *args, **kwargs)

    @property
    def code(self) -> int:
        return self._code


class Wialon(wialon.api.Wialon):
    def call(self, *argc, **kwargs) -> dict[str, typing.Any]:
        try:
            return super().call(*argc, **kwargs)
        except wialon.api.WialonError as e:
            raise WialonAPIError(e)


class WialonSession:
    def __init__(
        self,
        token: str | None = None,
        sid: str | None = None,
        scheme: str = "https",
        host: str = "hst-api.wialon.com",
        port: int = 443,
    ) -> None:
        """
        Starts or continues a Wialon API session.

        :param token: An optional Wialon API token. Default is :confval:`WIALON_TOKEN`.
        :type token: :py:obj:`str` | :py:obj:`None`
        :param sid: An optional Wialon API session id. If provided, the session is continued.
        :type sid: :py:obj:`str` | :py:obj:`None`
        :param scheme: HTTP request scheme to use. Default is ``"https"``.
        :type scheme: :py:obj:`str`
        :param host: Wialon API host url. Default is ``"hst-api.wialon.com"``.
        :type host: :py:obj:`str`
        :param port: Wialon API port. Default is ``443``.
        :type port: :py:obj:`int`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """

        self._token = token or os.getenv("WIALON_TOKEN")
        self._username = None
        self._uid = None
        self._wialon_api = Wialon(
            scheme=scheme, host=host, port=port, sid=sid, token=self.token
        )

    def __str__(self) -> str:
        return f"Session #{self.id}"

    def __repr__(self) -> str:
        return f"{self.__class__}(sid={self.id})"

    def __enter__(self) -> "WialonSession":
        """
        Logs into the Wialon API using :py:meth:`login`.

        :raises AssertionError: If the session's Wialon API :py:attr:`token` wasn't set.
        :returns: A valid Wialon API session.
        :rtype: :py:obj:`~terminusgps.wialon.session.WialonSession`

        """
        assert self.token, "Wialon API token wasn't set."
        self.login(self.token)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """
        Logs out of the session by calling :py:meth:`logout`.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.logout()

    @property
    def wialon_api(self) -> Wialon:
        return self._wialon_api

    @property
    def uid(self) -> str | None:
        """
        A Wialon user ID this session is operating as.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`
        """
        return self._uid

    @property
    def username(self) -> str | None:
        """
        A Wialon username the session is operating as.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._username

    @property
    def id(self) -> str | None:
        """
        Shortcut property for :py:attr:`WialonSession.wialon_api.sid`.

        Returns :py:obj:`None` if the session wasn't logged in.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self.wialon_api.sid

    @property
    def token(self) -> str:
        """
        A Wialon API token set during :py:meth:`WialonSession.__init__`.

        Default token value is :confval:`WIALON_TOKEN`.

        :type: :py:obj:`str`
        :value: :confval:`WIALON_TOKEN`

        """
        return str(self._token)

    def login(self, token: str, flags: int | None = None) -> str:
        """
        Logs into the Wialon API and starts a new session.

        :param token: An active Wialon API token.
        :type token: :py:obj:`str`
        :param flags: A login response flag integer.
        :type flags: :py:obj:`int`
        :raises WialonError: If the login fails.
        :raises AssertionError: If the login token was not set.
        :returns: The new session id.
        :rtype: :py:obj:`str`

        """
        try:
            response = self.wialon_api.token_login(
                **{"token": token, "fl": flags if flags else 0x2}
            )
            self._set_login_response(response)
            return response.get("eid", "")
        except (wialon.api.WialonError, ValueError):
            print("Failed to login to the Wialon API.")
            raise

    def logout(self) -> None:
        """
        Logs out of the Wialon API session.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        sid = self.wialon_api.sid
        response = self.wialon_api.core_logout({})

        if response.get("error") != 0:
            print(
                f"Failed to properly logout of session #{sid}: '{response.get('message')}'"
            )
        self.wialon_api.sid = None

    def _set_login_response(self, login_response: dict | None = None) -> None:
        """
        Sets the Wialon API session's attributes based on a login response.

        :param login_response: A dictionary returned from :py:meth:`login`.
        :type login_response: :py:obj:`dict`
        :raises ValueError: If ``login_response`` wasn't provided.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if login_response is None:
            raise ValueError(f"Login response is required, got '{login_response}'")

        self.wialon_api.sid = login_response.get("eid")
        self._uid = login_response.get("user", {}).get("id")
        self._username = login_response.get("au")
