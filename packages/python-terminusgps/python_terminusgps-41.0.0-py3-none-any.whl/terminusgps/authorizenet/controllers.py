import typing

from authorizenet.apicontrollersbase import APIOperationBase

from .auth import get_environment


def execute_controller(controller: APIOperationBase) -> dict[str, typing.Any] | None:
    """
    Executes an Authorizenet API controller and returns its response.

    :param controller: An Authorizenet API controller.
    :type controller: :py:obj:`~authorizenet.apicontrollersbase.APIOperationBase`
    :raises AuthorizenetControllerExecutionError: If the API call fails.
    :returns: An Authorizenet API response, if any.
    :rtype: :py:obj:`dict` | :py:obj:`None`

    """
    try:
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
    except Exception:
        response = None

    if response is not None and response.messages.resultCode != "Ok":
        raise AuthorizenetControllerExecutionError(
            message=response.messages.message[0]["text"].text,
            code=response.messages.message[0]["code"].text,
        )
    return response


class AuthorizenetControllerExecutor:
    """Allows objects to use :py:meth:`execute_controller` to execute Authorizenet API controllers."""

    @staticmethod
    def execute_controller(
        controller: APIOperationBase,
    ) -> dict[str, typing.Any] | None:
        """
        Executes an Authorizenet API controller and returns its response.

        :param controller: An Authorizenet API controller.
        :type controller: :py:obj:`~authorizenet.apicontrollersbase.APIOperationBase`
        :raises AuthorizenetControllerExecutionError: If the API call fails.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        return execute_controller(controller)


class AuthorizenetControllerExecutionError(Exception):
    """Raised when an Authorizenet API controller fails to execute."""

    def __init__(self, message: str, code: str, *args, **kwargs) -> None:
        """
        Sets :py:attr:`message` and :py:attr`code` for the exception.

        :param message: An Authorizenet API error message.
        :type message: :py:obj:`str`
        :param code: An Authorizenet API error code.
        :type code: :py:obj:`str`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        super().__init__(message, *args, **kwargs)
        self._message = message
        self._code = code

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    @property
    def message(self) -> str:
        """An Authorizenet API error message."""
        return self._message

    @property
    def code(self) -> str:
        """An Authorizenet API error code."""
        return self._code
