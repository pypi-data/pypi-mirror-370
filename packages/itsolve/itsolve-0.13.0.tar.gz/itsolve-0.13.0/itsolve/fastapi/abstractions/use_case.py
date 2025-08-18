from typing import Any, Protocol, TypeVar, runtime_checkable

ReturnType_co = TypeVar("ReturnType_co", covariant=True)


@runtime_checkable
class IUseCase(Protocol[ReturnType_co]):
    async def execute(self, *args: Any, **kwargs: Any) -> ReturnType_co: ...
