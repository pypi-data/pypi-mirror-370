from fastapi import WebSocket

from ..configuration import KEYCLOAK_OPENID


class WebSocketAuthMiddleware:
    """
    Custom middleware for WebSocket authentication.

    This class does not inherit from BaseHTTPMiddleware and is specifically
    designed to handle authentication for WebSocket connections by verifying
    a JWT token provided in the headers.

    Attributes:
        __auth__ (str): The name of the header expected to contain the
        authorization token.
    """

    __auth__ = 'authorization'

    async def unauthorised(self, websocket: WebSocket, code: int = 1008,
                           msg: str = 'Unauthorised'):
        """
        Closes the WebSocket connection with a specific close code and reason.

        Close code 1008 is used to indicate a policy violation or failed
        authentication.

        :param websocket: The WebSocket instance to close.
        :param code: The WebSocket close code (default is 1008).
        :param msg: The reason message for closing the connection (default is
        'Unauthorised').
        """
        await websocket.close(code=code, reason=msg)

    def decode_token(self, token: str):
        """
        Decodes a JWT token by stripping the 'Bearer ' prefix and using the
        decoding method configured in KEYCLOAK_OPENID.

        :param token: The full JWT token, possibly with a 'Bearer ' prefix.
        :return: The decoded payload from the JWT token.
        :raises: Exceptions raised by KEYCLOAK_OPENID.decode_token if the
        token is invalid.
        """
        token_ = token.replace('Bearer ', '')
        payload = KEYCLOAK_OPENID.decode_token(token_)
        return payload

    def is_auth(self, token: str) -> str:
        """
        Verifies the authenticity of the JWT token.

        Attempts to decode the token and, if valid, returns the payload.
        If an error occurs, logs an authentication failure message and returns
        an empty string.

        :param token: The JWT token to verify.
        :return: The decoded payload if valid, otherwise an empty string.
        """
        try:
            decode_token = self.decode_token(token)
            return decode_token
        except Exception as e:
            print(f"Authentication failed: {e}")
            return ''
