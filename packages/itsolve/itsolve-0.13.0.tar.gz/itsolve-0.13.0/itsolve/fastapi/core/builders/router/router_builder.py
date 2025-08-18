from __future__ import annotations

from typing import Any

from authx import AuthX
from casbin import Enforcer

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from itsolve.fastapi.integrations.casbin import apply_permissions

from .auth_route import AuthRouteMeta
from .default_user_payload_schema import DefaultTUserPayload


class APIRouterBuilder(APIRouter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.is_auth_router: bool = False

    def apply_version(self, version: str) -> APIRouterBuilder:
        if not version.startswith("v"):
            raise ValueError("Version must start with 'v'")
        self.version = version
        return self

    def apply_auth(
        self,
        jwt_service: AuthX,
        user_payload_schema: type[DefaultTUserPayload] = DefaultTUserPayload,
        auth_schema: HTTPBearer = HTTPBearer(),
    ) -> APIRouterBuilder:
        self.route_class = AuthRouteMeta(
            user_payload_schema=user_payload_schema,
            jwt_service=jwt_service,
        )

        self.dependencies.append(Depends(auth_schema))

        self.is_auth_router = True
        return self

    def apply_permissions(
        self,
        enforcer: Enforcer,
        resource: str | None = None,
    ) -> APIRouterBuilder:
        if not self.is_auth_router:
            raise ValueError("Permissions can only be applied to auth routers")
        self.dependencies.append(
            Depends(
                apply_permissions(
                    enforcer,
                    resource or self.prefix.replace("/", ""),
                )
            )
        )

        return self
