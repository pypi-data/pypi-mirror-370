from typing import Callable

from casbin import AsyncEnforcer, Enforcer

from fastapi import Request
from itsolve.fastapi.core.exceptions import PermissionsDeniedError


def apply_permissions(
    enforcer: AsyncEnforcer | Enforcer,
    obj: str | None = None,
    act: str | None = None,
) -> Callable:
    def wrapper(request: Request) -> Request:
        act_cfg = dict(
            GET="read",
            POST="write",
            PATCH="write",
            PUT="write",
            DELETE="delete",
        )
        sub = request.state.user.role
        _obj = obj or request.url.path.split("/")[1]  # TODO: add version
        _act = act or act_cfg.get(request.method, act)
        if enforcer.enforce(sub, _obj, _act):
            return request
        else:
            raise PermissionsDeniedError(
                ctx=dict(
                    sub=sub,
                    obj=_obj,
                    act=_act,
                ),
            )

    return wrapper
