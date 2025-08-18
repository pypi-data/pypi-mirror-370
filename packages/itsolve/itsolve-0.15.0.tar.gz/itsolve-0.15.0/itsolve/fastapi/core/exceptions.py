import json
from typing import Any, Callable

from loguru import logger
from pydantic import BaseModel, TypeAdapter

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder


class ErrorDetails(BaseModel):
    """
    Default Error model for API
    Type is key for string
    type: "general.errors.doesnt_exists"
    """

    type: str
    description: str | None = None
    ctx: dict | None = None


class AppError(HTTPException):
    def __init__(
        self,
        error: str,
        description: str | None = None,
        ctx: dict | None = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        ta = TypeAdapter(list[ErrorDetails])
        errors = ta.validate_python(
            [{"type": error, "description": description, "ctx": ctx}]
        )
        super().__init__(
            status_code=status_code,
            detail=jsonable_encoder(errors, exclude_none=True),
        )


class GlobalAppError(AppError):
    STATUS_CODE: int = status.HTTP_400_BAD_REQUEST
    ERROR: str
    DESCRIPTION: str | None = None
    CTX_EXAMPLE_STRUCTURE: dict[str, Any] = {}

    def __init__(self, message: str | None = None, ctx: dict | None = None) -> None:
        super().__init__(
            status_code=self.STATUS_CODE,
            description=message or self.DESCRIPTION or "",
            error=self.ERROR,
            ctx=ctx,
        )


class DeclareModuleAppError(GlobalAppError):
    MODULE: str

    def __init__(self, message: str | None = None, ctx: dict | None = None) -> None:
        self.ERROR = f"{self.MODULE}.{self.ERROR}"
        super().__init__(message, ctx)


class NotFoundInstanceError(GlobalAppError):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    ERROR = "not_found"
    DESCRIPTION = "Server can not find such instance"


class AlreadyExistsInstanceError(GlobalAppError):
    STATUS_CODE = status.HTTP_409_CONFLICT
    ERROR = "already_exists"
    DESCRIPTION = "Such instance exists"


class ValidationDataInstanceError(GlobalAppError):
    STATUS_CODE = status.HTTP_422_UNPROCESSABLE_ENTITY
    ERROR = "validation_data"
    DESCRIPTION = "Wrong data sent"


class PermissionsDeniedError(GlobalAppError):
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    ERROR = "permissions_denied"
    DESCRIPTION = "Permissions denied"
    CTX_EXAMPLE_STRUCTURE = {
        "sub": "sub:string",
        "obj": "obj:string (resource)",
        "act": "act:string",
    }


class UnknownError(GlobalAppError):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    ERROR = "unknown"
    DESCRIPTION = "Something went wrong"

    def __init__(self, module: str | None = None, ctx: dict | None = None) -> None:
        self.ERROR = f"{module}.{self.ERROR}" if module else self.ERROR
        super().__init__(ctx=ctx)


class ResourceError(GlobalAppError):
    STATUS_CODE: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, module: str | None = None, ctx: dict | None = None) -> None:
        self.ERROR = f"{module}.{self.ERROR}" if module else self.ERROR
        super().__init__(ctx=ctx)


class ResourceCreateError(ResourceError):
    ERROR: str = "create_error"
    DESCRIPTION = "Creation failed"


class ResourceRetrieveError(ResourceError):
    ERROR: str = "retrieve_error"
    DESCRIPTION = "Error occurred while retrieving"


class ResourceUpdateError(ResourceError):
    ERROR: str = "update_error"
    DESCRIPTION = "Error occurred while updating"


class ResourceDeleteError(ResourceError):
    ERROR: str = "delete_error"
    DESCRIPTION = "Error occurred while deleting"


class JwtSettingsError(Exception):
    pass


class ConfigurationError(Exception):
    pass


def uncaught_error(
    exc: type[GlobalAppError] | GlobalAppError, msg: str | None = None
) -> Callable:
    def decorator(func: Callable) -> Callable:
        async def wrapper(obj: Any, *args: Any, **kwargs: Any) -> Any:
            try:
                return await func(obj, *args, **kwargs)
            except Exception as e:
                error_msg = msg or "Uncaught error occurred"
                ctx_info = dict(
                    args=args,
                    kwargs=kwargs,
                    module=func.__module__,
                    method=func.__name__,
                )
                logger.warning(
                    f"{error_msg} ({e}) | ctx: {json.dumps(ctx_info, default=str)}"
                )

                if isinstance(exc, type):
                    raise exc(ctx=dict(args=args, kwargs=kwargs)) from e
                raise exc from e

        return wrapper

    return decorator
