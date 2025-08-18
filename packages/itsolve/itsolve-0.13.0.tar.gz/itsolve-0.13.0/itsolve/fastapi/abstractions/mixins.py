from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

Entity = TypeVar("Entity")
ID = TypeVar("ID")
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)


class ICreateMixin[Entity, CreateSchema](Protocol):
    """
    Provide `create` method

    Example:
        ```python
        class IYourRepo(ICreateMixin[Entity, YourCreateSchema]):
        ```

    Generic:
        `Entity`: Entity

        `CreateSchema`: Pydantic model

    Args:
        `data`: Pydantic model

    Returns:
        Entity
    """

    async def create(self, data: CreateSchema) -> Entity: ...


class IRetrieveMixin[Entity, ID](Protocol):
    """
    Provide `retrieve` and `retrieve_by` methods

    Example:
        ```python
        class IYourRepo(IRetrieveMixin[Entity, int]):
        ```

    Generics:
        `Entity`: Entity

        `ID`: Primary key type

    Args:
        `retrieve` - `id`: Primary key

        `retrieve_by` - `**filters`: Filters
    Returns:
        Entity
    """

    async def retrieve(self, id: ID) -> Entity: ...

    async def retrieve_by(self, **filters: Any) -> Entity: ...


class IUpdateMixin[Entity, ID, UpdateSchema](Protocol):
    """
    Provide `update` method

    Example:
        ```python
        class IYourRepo(IUpdateMixin[Entity, int, YourUpdateSchema]):
        ```

    Generics:
        `Entity`: Entity

        `UpdateSchema`: Pydantic model

        `ID`: Primary key

    Args:
        `id`: Primary key

        `data`: Pydantic model

    Returns:
        Entity
    """

    async def update(self, id: ID, data: UpdateSchema) -> Entity: ...


class IDeleteMixin[ID](Protocol):
    """
    Provide `delete` method

    Example:
        ```python
        class IYourRepo(IDeleteMixin[int]):
        ```

    Generics:
        `ID`: Primary key

    Args:
        `id`: Primary key

    Returns:
        Primary key
    """

    async def delete(self, id: ID) -> ID: ...


class FilterMixin[Entity](Protocol):
    """
    Provide `filter` method

    Example:
        ```python
        class IYourRepo(FilterMixin[Entity]):
        ```

    Generics:
        `Entity`: Entity

    Args:
        `**filters`: Filters

    Returns:
        List of entities
    """

    async def filter(self, **filters: Any) -> list[Entity]: ...


class IReadableMixin[Entity, ID](IRetrieveMixin[Entity, ID]):
    """
    Provide `retrieve` and `retrieve_by` methods

    Example:
        ```python
        class IYourRepo(IReadableMixin[Entity, int]):
        ```

    Generics:
        `Entity`: Entity

        `ID`: Primary key type

    Args:
        `retrieve` - `id`: Primary key

        `retrieve_by` - `**filters`: Filters

    Returns:
        Entity
    """


class IWritableMixin[Entity, ID, CreateSchema, UpdateSchema](
    ICreateMixin[Entity, CreateSchema],
    IUpdateMixin[Entity, ID, UpdateSchema],
):
    """
    Provide `create` and `update` methods

    Example:
        ```python
        class IYourRepo(
            IWritableMixin[
                Entity,
                int,
                YourCreateSchema,
                YourUpdateSchema
            ]
        ):
        ```

    Generics:
        `Entity`: Entity

        `ID`: Primary key

        `CreateSchema`: Pydantic model

        `UpdateSchema`: Pydantic model

    Args:
        `create` - `data`: Pydantic model

        `update` - `id`: Primary key, `data`: Pydantic model

    Returns:
        Entity
    """


class ICRUDMixin[Entity, ID, CreateSchema, UpdateSchema](
    ICreateMixin[Entity, CreateSchema],
    IRetrieveMixin[Entity, ID],
    IUpdateMixin[Entity, ID, UpdateSchema],
    IDeleteMixin[ID],
):
    """
    Provide `create`, `retrieve`, `update` and `delete` methods

    Example:
        ```python
        class IYourRepo(
            ICRUDMixin[Entity, int, YourCreateSchema, YourUpdateSchema]
        ):
        ```

    Generics:
        `Entity`: Entity

        `ID`: Primary key

        `CreateSchema`: Pydantic model

        `UpdateSchema`: Pydantic model

    Args:
        `create` - `data`: Pydantic model

        `retrieve` - `id`: Primary key

        `retrieve_by` - `**filters`: Filters

        `update` - `id`: Primary key, `data`: Pydantic model

        `delete` - `id`: Primary key

    Returns:
        Entity
    """
