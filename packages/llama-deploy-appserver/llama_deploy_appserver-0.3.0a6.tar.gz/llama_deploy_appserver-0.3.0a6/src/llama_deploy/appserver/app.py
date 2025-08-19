import argparse
import logging
import os
import threading
import time
import webbrowser
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from llama_deploy.appserver.deployment_config_parser import (
    get_deployment_config,
)
from llama_deploy.appserver.routers.deployments import (
    create_base_router,
    create_deployments_router,
)
from llama_deploy.appserver.routers.ui_proxy import (
    create_ui_proxy_router,
    mount_static_files,
)
from llama_deploy.appserver.settings import configure_settings, settings
from llama_deploy.appserver.workflow_loader import (
    _exclude_venv_warning,
    build_ui,
    find_python_pyproject,
    inject_appserver_into_target,
    install_ui,
    load_environment_variables,
    load_workflows,
    start_dev_ui_process,
)
from prometheus_fastapi_instrumentator import Instrumentator

from .deployment import Deployment
from .process_utils import run_process
from .routers import health_router
from .stats import apiserver_state

logger = logging.getLogger("uvicorn.info")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    apiserver_state.state("starting")
    config = get_deployment_config()

    workflows = load_workflows(config)
    deployment = Deployment(workflows)
    base_router = create_base_router(config.name)
    deploy_router = create_deployments_router(config.name, deployment)
    app.include_router(base_router)
    app.include_router(deploy_router)
    # proxy UI in dev mode
    if config.ui is not None:
        if settings.proxy_ui:
            ui_router = create_ui_proxy_router(config.name, config.ui.port)
            app.include_router(ui_router)
        else:
            # otherwise serve the pre-built if available
            mount_static_files(app, config, settings)

    apiserver_state.state("running")
    yield

    apiserver_state.state("stopped")


app = FastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)

# Configure CORS middleware if the environment variable is set
if not os.environ.get("DISABLE_CORS", False):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"],
    )

app.include_router(health_router)


def open_browser_async(host: str, port: int) -> None:
    def _open_with_delay() -> None:
        time.sleep(1)
        webbrowser.open(f"http://{host}:{port}")

    threading.Thread(target=_open_with_delay).start()


def prepare_server(
    deployment_file: Path | None = None,
    install: bool = False,
    build: bool = False,
) -> None:
    configure_settings(deployment_file_path=deployment_file)
    load_environment_variables(get_deployment_config(), settings.config_parent)
    if install:
        config = get_deployment_config()
        inject_appserver_into_target(config, settings.config_parent)
        install_ui(config, settings.config_parent)
    if build:
        build_ui(settings.config_parent, get_deployment_config())


def start_server(
    proxy_ui: bool = False,
    reload: bool = False,
    cwd: Path | None = None,
    deployment_file: Path | None = None,
    open_browser: bool = False,
) -> None:
    # Configure via environment so uvicorn reload workers inherit the values
    configure_settings(
        proxy_ui=proxy_ui,
        app_root=cwd,
        deployment_file_path=deployment_file,
        reload=reload,
    )
    load_environment_variables(get_deployment_config(), settings.config_parent)

    ui_process = None
    if proxy_ui:
        ui_process = start_dev_ui_process(
            settings.config_parent, settings.port, get_deployment_config()
        )
    try:
        if open_browser:
            open_browser_async(settings.host, settings.port)

        uvicorn.run(
            "llama_deploy.appserver.app:app",
            host=settings.host,
            port=settings.port,
            reload=reload,
        )
    finally:
        if ui_process is not None:
            ui_process.terminate()


def start_server_in_target_venv(
    proxy_ui: bool = False,
    reload: bool = False,
    cwd: Path | None = None,
    deployment_file: Path | None = None,
    open_browser: bool = False,
) -> None:
    cfg = get_deployment_config()
    path = find_python_pyproject(cwd or Path.cwd(), cfg)

    args = ["uv", "run", "python", "-m", "llama_deploy.appserver.app"]
    if proxy_ui:
        args.append("--proxy-ui")
    if reload:
        args.append("--reload")
    if deployment_file:
        args.append("--deployment-file")
        args.append(str(deployment_file))
    if open_browser:
        args.append("--open-browser")
    # All the streaming/PTY/pipe handling is centralized
    ret = run_process(
        args,
        cwd=path,
        env=None,
        line_transform=_exclude_venv_warning,
    )

    if ret != 0:
        raise SystemExit(ret)


if __name__ == "__main__":
    print("starting server")
    parser = argparse.ArgumentParser()
    parser.add_argument("--proxy-ui", action="store_true")
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--deployment-file", type=Path)
    parser.add_argument("--open-browser", action="store_true")

    args = parser.parse_args()
    start_server(
        proxy_ui=args.proxy_ui,
        reload=args.reload,
        deployment_file=args.deployment_file,
        open_browser=args.open_browser,
    )
