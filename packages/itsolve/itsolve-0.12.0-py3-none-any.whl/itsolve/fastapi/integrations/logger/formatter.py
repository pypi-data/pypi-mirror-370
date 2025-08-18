from __future__ import annotations

from pprint import pformat
from typing import TYPE_CHECKING, Any, Callable

from itsolve.fastapi.settings import LoggerSettings

if TYPE_CHECKING:
    from loguru import Record


def formatter(
    time_format: str,
    settings: LoggerSettings,
    observability: bool = False,
) -> Callable[[Record], Any]:
    def format_function(record: Record) -> str:
        time = "<green>{time:" + time_format + "}</green> | "
        def_format = (
            time + "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:"
            "<cyan>{function}</cyan>:"
            "<cyan>{line}</cyan> "
            "<magenta>[{extra[logger_name]}]</magenta>"
            # "<blue>context: {extra}</blue>"
        )
        if observability:
            def_format += (
                " [<red>trace_id={extra[otelTraceID]} "
                + "span_id={extra[otelSpanID]} "
                + "resource.service.name={extra[otelServiceName]}</red>]"
            )

        def_format += " - <level>{message}</level>{exception}"
        ctx = record["extra"].get("ctx", None)
        user = record["extra"].get("user", None)
        if not ctx and not user:
            return def_format + "\n"
        level = record["level"].name
        record["extra"]["ctx"] = pformat(
            ctx,
            width=settings.ctx_width,
            indent=settings.ctx_indent,
            underscore_numbers=settings.ctx_underscore_numbers,
            compact=settings.ctx_compact,
            depth=None if level == "DEBUG" else settings.ctx_depth,
        )
        return_formate = def_format
        if user:
            user_format = f"<yellow>User: {user}</yellow>"
            return_formate += f" ({user_format})"
        context_format = "<green>{extra[ctx]}</green>"
        # exeption_format = "<red>{exception}</red>" TODO: Add exception
        if ctx:
            return_formate += "\n" + context_format
        return return_formate + "\n"

    return format_function
