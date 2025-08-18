from typing import TypeVar

from .repository import Repository

IRepo = TypeVar("IRepo", bound=Repository)


class Service[IRepo]:
    repo: IRepo

    def __init__(self, repo: IRepo) -> None:
        self.repo = repo
