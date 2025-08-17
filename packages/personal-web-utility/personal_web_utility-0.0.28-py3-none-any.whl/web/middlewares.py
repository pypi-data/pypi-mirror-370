from contextvars import ContextVar

from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send

from web.exceptions import ProcessingException

USER_CONTEXT_KEY = "user_context"


class UserContext:
    id: str
    username: str
    session_id: str
    roles: list[str]


user_context_ctx_var: ContextVar[UserContext] = ContextVar(USER_CONTEXT_KEY, default=UserContext())


def get_user_context() -> UserContext:
    return user_context_ctx_var.get()


def parse_headers(headers: Headers):
    id = headers.get("X-MACUKA-ID")
    username = headers.get("X-MACUKA-USERNAME")
    roles = headers.get("X-MACUKA-ROLES")
    cookies = headers.get('cookie').split(';')

    if roles is None or username is None or roles is None:
        return None

    session_id = None
    for cookie in cookies:
        typed_cookie: str = cookie
        if typed_cookie.upper().count("X_MACUKA_SESSION") == 1:
            session_id = typed_cookie.split('=')[1]
            break
    if session_id is None:
        raise ProcessingException('session it not found')

    context = UserContext()
    context.id = id.split(":")[0]
    context.username = username.split(":")[0]
    context.roles = roles.split(":")[0].split(",")
    context.session_id = session_id
    return context


class UsernameMiddleware:
    def __init__(
            self,
            app: ASGIApp,
    ) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)

        context = parse_headers(headers)

        if context is None:
            await self.app(scope, receive, send)
            return

        user_context = user_context_ctx_var.set(context)

        await self.app(scope, receive, send)

        user_context_ctx_var.reset(user_context)
