from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi.routing import APIRoute

from .default_user_payload_schema import DefaultTUserPayload

if TYPE_CHECKING:
    from typing import Any, Callable, Coroutine

    from authx import AuthX

    from fastapi import Request, Response


class AuthRouteMeta(type):
    def __new__(
        cls,
        jwt_service: AuthX,
        user_payload_schema: type[DefaultTUserPayload],
    ) -> type[AuthRoute]:
        klass = AuthRoute
        klass.USER_PAYLOAD_SCHEMA = user_payload_schema
        klass.JWT_SERVICE = jwt_service
        return klass


class AuthRoute(APIRoute):
    USER_PAYLOAD_SCHEMA: type[DefaultTUserPayload]
    JWT_SERVICE: AuthX

    def get_route_handler(
        self,
    ) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_handler = super().get_route_handler()

        async def handler(request: Request) -> Response:
            token_payload = await self.JWT_SERVICE.access_token_required(request)
            user = self.USER_PAYLOAD_SCHEMA.model_validate(
                token_payload, from_attributes=True
            )
            request.state.user = user
            return await original_handler(request)

        return handler
