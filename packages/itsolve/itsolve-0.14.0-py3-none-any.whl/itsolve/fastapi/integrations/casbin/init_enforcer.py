import csv
from pathlib import Path
from typing import TypedDict

import httpx
from casbin import Enforcer

# from casbin_async_sqlalchemy_adapter import Adapter
from loguru import logger

from itsolve.fastapi.settings import PermissionsSettings


class Policy(TypedDict):
    subject: str
    action: str
    object: str


# async def async_init_enforcer(
#     adapter: Adapter,
#     enforcer: AsyncEnforcer,
#     rules_generator: Callable[..., Awaitable[None]] | None = None,
# ) -> AsyncEnforcer:
#     await adapter.create_table()

#     if rules_generator:
#         await rules_generator()
#     enforcer.enable_auto_save(True)
#     await enforcer.load_policy()
#     return enforcer


def sync_init_enforcer(settings: PermissionsSettings) -> Enforcer:
    if not settings.mock_policy:
        response = httpx.get(settings.RESOURCE_URL)
        data: list[Policy] = response.json()
        csv_data = [
            ["p", policy["subject"], policy["object"], policy["action"]]
            for policy in data
        ]
        with open(  # noqa: PTH123
            str(Path.joinpath(Path.cwd(), settings.file_policy_name)),
            "w",
            newline="",
        ) as file:
            writer = csv.writer(file)
            writer.writerows(csv_data)
        logger.info(f"File {settings.file_policy_name} loaded")
    e = Enforcer(
        str(Path.joinpath(Path.cwd(), settings.file_model_name)),
        str(Path.joinpath(Path.cwd(), settings.file_policy_name)),
    )
    e.load_policy()
    return e
