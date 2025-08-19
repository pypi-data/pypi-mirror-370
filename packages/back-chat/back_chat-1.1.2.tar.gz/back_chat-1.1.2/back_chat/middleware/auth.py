from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from ..configuration import KEYCLOAK_OPENID


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle authentication for incoming HTTP requests.

    This middleware intercepts requests and determines if they need
    authentication based on a predefined list of paths that can bypass
    authentication (e.g., docs, health check).

    If authentication is required, it checks for the presence of a valid API
    key or a valid authorization token (JWT), decoding it via Keycloak OpenID
    service.

    Attributes:
        __jump_paths__ (list): List of URL paths that do not require
        authentication.
        __auth__ (str): Header key name for authorization token.
    """

    __jump_paths__ = ['/docs', '/openapi.json', '/redoc',
                      '/health', '/favicon.ico']
    __auth__ = 'authorization'

    def __init__(self, *args, **kwargs):
        """
        Initialize the middleware by calling the parent class initializer.
        """
        super().__init__(*args, **kwargs)

    @staticmethod
    def unauthorised(
            code: int = 401, msg: str = 'Unauthorised') -> JSONResponse:
        """
        Return a JSON response indicating an unauthorized access attempt.

        :param code: HTTP status code to return (default 401).
        :param msg: Message to include in the response body
        (default 'Unauthorised').
        :return: JSONResponse with status code and message.
        """
        return JSONResponse(status_code=code, content=msg)

    def _is_jump_url_(self, request: Request) -> bool:
        """
        Check if the requested URL path is in the list of paths that do not
        require auth.

        :param request: The incoming HTTP request.
        :return: True if the path should bypass authentication, False otherwise.
        """
        return request.url.path in self.__jump_paths__

    def decode_token(self, token: str):
        """
        Decode a JWT token after stripping 'Bearer ' prefix.

        :param token: Raw token string from the authorization header.
        :return: Decoded token payload (usually a dict).
        """
        token_ = token.replace('Bearer ', '')
        payload = KEYCLOAK_OPENID.decode_token(token_)
        return payload

    def get_header_token(self, request: Request) -> str:
        """
        Get the authorization token from the request headers.

        :param request: The incoming HTTP request.
        :return: Authorization header value or empty string if missing.
        """
        return request.headers.get(self.__auth__, '')

    def get_user_config(self, request: Request) -> dict | None:
        """
        Extract user configuration by decoding the JWT token from the request.

        :param request: The incoming HTTP request.
        :return: Decoded token payload dict if valid, else None.
        """
        token = self.get_header_token(request)
        try:
            decode_token = self.decode_token(token)
            return decode_token
        except Exception:
            return None

    def is_auth(self, request: Request) -> dict | None:
        """
        Check whether the request is authenticated.

        Currently implemented by trying to get user config from token.

        :param request: The incoming HTTP request.
        :return: User configuration dict if authenticated, else None.
        """
        return self.get_user_config(request)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process incoming HTTP request, enforcing authentication if required.

        If the request path is in the bypass list, it proceeds without checks.
        Otherwise, it verifies authentication and returns an unauthorized
        response if authentication fails.

        :param request: The incoming HTTP request.
        :param call_next: The next middleware or request handler callable.
        :return: Response from next handler or unauthorized response.
        """
        if self._is_jump_url_(request):
            return await call_next(request)

        response = self.unauthorised()

        if self.is_auth(request):
            response = await call_next(request)

        return response
