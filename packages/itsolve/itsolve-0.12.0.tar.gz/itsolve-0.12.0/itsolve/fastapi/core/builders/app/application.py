from __future__ import annotations

import re
from collections import Counter
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from loguru import logger
from starlette.types import Lifespan

from authx import AuthX
from authx._internal._error import _ErrorHandler  # type: ignore[unused-ignore]
from authx.exceptions import AuthXException, JWTDecodeError
from itsolve.fastapi.core.exceptions import AppError
from itsolve.fastapi.integrations.logger import configure_logger
from itsolve.fastapi.integrations.observability import setting_otlp


def register_ui_docs_routes(app: FastAPI) -> FastAPI:
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html() -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url=app.root_path
            + (app.openapi_url if app.openapi_url else "/openapi.json"),
            title=app.title,
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5.20.0/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5.20.0/swagger-ui.css",
            swagger_favicon_url="https://unpkg.com/swagger-ui-dist@5.20.0/favicon-32x32.png",
        )

    @app.get("/redoc", include_in_schema=False)
    async def custom_redoc_ui_html() -> HTMLResponse:
        return get_redoc_html(
            openapi_url=app.root_path
            + (app.openapi_url if app.openapi_url else "/openapi.json"),
            title=app.title,
            redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
            redoc_favicon_url="https://unpkg.com/swagger-ui-dist@5.20.0/favicon-32x32.png",
        )

    return app


class AppBuilder:
    app: FastAPI

    def __init__(self, settings: Any) -> None:
        self.settings = settings
        self.init_enforcer: Callable | None = None

    def check_app_configuration(self) -> AppBuilder:
        return self

    def configure_jwt_service[UserOrmT](
        self,
        *,
        jwt_service: AuthX[UserOrmT],
    ) -> AppBuilder:
        async def custom_error_handler(
            self: _ErrorHandler,
            request: Request,  # noqa: ARG001
            exc: AuthXException,
            status_code: int,
            message: str | None = None,
        ) -> JSONResponse:
            if message is None:
                default_message = str(exc)
                attr_name = f"MSG_{exc.__class__.__name__}"
                message = getattr(self, attr_name, default_message)
            if isinstance(exc, JWTDecodeError):
                error_code = "jwt_decode_error"
            else:
                error_code = re.sub(
                    r"(\w)([A-Z])", r"\1_\2", exc.__class__.__name__
                ).lower()
            raise AppError(
                error=error_code,
                description=message,
                status_code=status_code,
                ctx={},
            )

        jwt_service.handle_errors(app=self.app)
        _ErrorHandler._error_handler = custom_error_handler
        logger.info("JWT service configured")
        return self

    def configure_logger(self) -> AppBuilder:
        configure_logger(
            name=self.settings.project.name,
            settings=self.settings.logger,
            observability=self.settings.observability.enabled,
            env=self.settings.MODE,
        )
        logger.info("Logger configured")
        return self

    def collect_routers(self) -> AppBuilder:
        import importlib
        from pathlib import Path

        def convert_path_to_python_import(path: str) -> str:
            return path.replace("\\", ".").replace("/", ".").replace(".py", "")

        routers = Path("src").rglob("v*")
        counter = Counter[str]()
        for file in routers:
            path = convert_path_to_python_import(str(file))
            module = importlib.import_module(path)
            version = file.name
            for r in module.__all__:
                router = importlib.import_module(
                    convert_path_to_python_import(str(file.joinpath(r)))
                ).router
                if not hasattr(router, "version") or not router.version:
                    logger.warning(f"Router version not found: {version}")
                elif version == router.version:
                    self.app.include_router(
                        router, prefix=f"/{version}", tags=[version]
                    )
                    counter[version] += 1
                else:
                    logger.warning(
                        f"Router version mismatch: \
                        {version} != {router.version}"
                    )
        routers = Path().rglob("src/**/router.py")
        for file in routers:
            path = convert_path_to_python_import(str(file))
            module = importlib.import_module(path)
            if "router" in module.__dict__:
                counter[file.parent.name] += 1
                router = module.router
                self.app.include_router(router, prefix=self.settings.server.prefix)
        logger.info(
            "Routers collected",
            ctx={"amount": counter.total(), **dict(counter)},
        )
        return self

    def run(self) -> None:
        import uvicorn

        uvicorn.run(
            "main:app",
            host=self.settings.server.host,
            port=self.settings.server.port,
            reload=self.settings.server.reload,
            workers=self.settings.server.workers,
            proxy_headers=True,
            log_config=None,
        )

    def init_fastapi_app(
        self,
        *,
        override_docs_load: bool = False,
        lifespan: Lifespan[FastAPI] | None = None,
    ) -> AppBuilder:
        self.app = FastAPI(
            lifespan=lifespan or self.lifespan,
            title=self.settings.project.name,
            version=self.settings.project.version,
            summary=self.settings.project.description,
            description=self.settings.project.description,
            docs_url=None if override_docs_load else "/docs",
            redoc_url=None if override_docs_load else "/redoc",
            root_path=self.settings.server.root_path,
            root_path_in_servers=self.settings.server.root_path_in_servers,
            openapi_url=f"{self.settings.server.prefix}/openapi.json",
        )
        if override_docs_load:
            self.app = register_ui_docs_routes(self.app)

        return self

    def configure_cors_headers(
        self,
    ) -> AppBuilder:
        if self.app is None:
            raise ValueError("FastAPI app not initialized")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.settings.server.allow_origins,
            allow_credentials=self.settings.server.allow_credentials,
            allow_methods=self.settings.server.allow_methods,
            allow_headers=self.settings.server.allow_headers,
        )
        logger.info("CORDS Middleware was registered")
        return self

    def configure_enforcer(self, init_enforcer: Callable) -> AppBuilder:
        self.init_enforcer = init_enforcer
        return self

    def configure_observability(self) -> AppBuilder:
        if self.settings.observability.enabled:
            # Setting OpenTelemetry exporter
            setting_otlp(
                self.app,
                self.settings.project.name,
                self.settings.observability.otel_exporter_otlp_endpoint,
            )
        return self

    @asynccontextmanager
    async def lifespan(self, _: FastAPI) -> AsyncGenerator[None]:  # noqa: ARG001
        logger.info(
            f"Application start: http://{self.settings.server.host}:{self.settings.server.port}"
        )
        logger.info(
            f"Swagger DOCS: http://{self.settings.server.host}:{self.settings.server.port}/docs"
        )
        logger.info(
            f"Redoc DOCS: http://{self.settings.server.host}:{self.settings.server.port}/redoc"
        )
        logger.info(
            "Info:",
            ctx={
                "name": self.settings.project.name,
                "version": self.settings.project.version,
            },
        )
        if self.init_enforcer and self.settings.permissions.enabled:
            self.init_enforcer()
            logger.info("Enforcer was registered")
        yield
        logger.info("Application end")
