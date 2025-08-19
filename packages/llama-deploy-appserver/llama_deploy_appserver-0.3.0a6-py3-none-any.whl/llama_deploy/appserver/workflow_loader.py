import functools
import importlib
import logging
import os
import socket
import subprocess
import sys
from importlib.metadata import version as pkg_version
from pathlib import Path

from dotenv import dotenv_values
from llama_deploy.appserver.deployment_config_parser import (
    DeploymentConfig,
)
from llama_deploy.appserver.process_utils import run_process, spawn_process
from llama_deploy.core.ui_build import ui_build_output_path
from packaging.version import InvalidVersion, Version
from workflows import Workflow

logger = logging.getLogger(__name__)

DEFAULT_SERVICE_ID = "default"


def load_workflows(config: DeploymentConfig) -> dict[str, Workflow]:
    """
    Creates WorkflowService instances according to the configuration object.

    """
    workflow_services = {}

    # Pre-compute per-service import info
    per_service: list[tuple[str, str]] = []
    for service_id, service_config in config.services.items():
        if service_config.import_path is None:
            continue
        raw_mod_path, workflow_name = service_config.import_path.split(":", 1)
        module_name = Path(raw_mod_path).name
        per_service.append((service_id, workflow_name))

    for service_id, workflow_name in per_service:
        import_path = config.services[service_id].import_path
        if import_path is None:
            continue
        raw_mod_path = import_path.split(":", 1)[0]
        module_name = Path(raw_mod_path).name

        module = importlib.import_module(module_name)

        if hasattr(module, workflow_name):
            workflow = getattr(module, workflow_name)
            if not isinstance(workflow, Workflow):
                logger.warning(
                    f"Workflow {workflow_name} in {module_name} is not a Workflow object",
                )
            workflow_services[service_id] = workflow
        else:
            logger.warning("Workflow %s not found in %s", workflow_name, module_name)

    if config.default_service:
        if config.default_service in workflow_services:
            workflow_services[DEFAULT_SERVICE_ID] = workflow_services[
                config.default_service
            ]
        else:
            msg = f"Service with id '{config.default_service}' does not exist, cannot set it as default."
            logger.warning(msg)

    return workflow_services


def load_environment_variables(config: DeploymentConfig, source_root: Path) -> None:
    """
    Load environment variables from the deployment config.
    """
    for service_id, service_config in config.services.items():
        env_vars = {**service_config.env} if service_config.env else {}
        for env_file in service_config.env_files or []:
            env_file_path = source_root / env_file
            values = dotenv_values(env_file_path)
            env_vars.update(**values)
        for key, value in env_vars.items():
            if value:
                os.environ[key] = value


@functools.cache
def are_we_editable_mode() -> bool:
    """
    Check if we're in editable mode.
    """
    # Heuristic: if the package path does not include 'site-packages', treat as editable
    top_level_pkg = "llama_deploy.appserver"
    try:
        pkg = importlib.import_module(top_level_pkg)
        pkg_path = Path(getattr(pkg, "__file__", "")).resolve()
        if not pkg_path.exists():
            return False

        return "site-packages" not in pkg_path.parts
    except Exception:
        return False


def inject_appserver_into_target(
    config: DeploymentConfig, source_root: Path, sdists: list[Path] | None = None
) -> None:
    """
    Ensures uv, and uses it to add the appserver as a dependency to the target app.
    - If sdists are provided, they will be installed directly for offline-ish installs (still fetches dependencies)
    - If the appserver is currently editable, it will be installed directly from the source repo
    - otherwise fetches the current version from pypi

    Args:
        config: The deployment config
        source_root: The root directory of the deployment
        sdists: A list of tar.gz sdists files to install instead of installing the appserver
    """
    path = _find_install_target(source_root, config)
    if path is None:
        logger.warning(
            "No python_dependencies and no root pyproject.toml; skipping dependency installation."
        )
        return
    logger.info(f"Installing ensuring venv at {path} and adding appserver to it")
    _ensure_uv_available()
    _add_appserver_if_missing(path, source_root, sdists=sdists)


def _get_installed_version_within_target(path: Path) -> Version | None:
    try:
        result = subprocess.check_output(
            [
                "uv",
                "run",
                "python",
                "-c",
                """from importlib.metadata import version; print(version("llama-deploy-appserver"))""",
            ],
            cwd=path,
        )
        try:
            return Version(result.decode("utf-8").strip())
        except InvalidVersion:
            return None
    except subprocess.CalledProcessError:
        return None


def _get_current_version() -> Version:
    return Version(pkg_version("llama-deploy-appserver"))


def _is_missing_or_outdated(path: Path) -> Version | None:
    """
    returns the current version if the installed version is missing or outdated, otherwise None
    """
    installed = _get_installed_version_within_target(path)
    current = _get_current_version()
    if installed is None or installed < current:
        return current
    return None


def _add_appserver_if_missing(
    path: Path,
    source_root: Path,
    save_version: bool = False,
    sdists: list[Path] | None = None,
) -> None:
    """
    Add the appserver to the venv if it's not already there.
    """

    if not (source_root / path / "pyproject.toml").exists():
        logger.warning(
            f"No pyproject.toml found at {source_root / path}, skipping appserver injection. The server will likely not be able to install your workflows."
        )
        return

    def ensure_venv(path: Path) -> Path:
        venv_path = source_root / path / ".venv"
        if not venv_path.exists():
            run_process(
                ["uv", "venv", str(venv_path)],
                cwd=source_root / path,
                prefix="[uv venv]",
                color_code="36",
            )
        return venv_path

    if sdists:
        run_process(
            ["uv", "pip", "install"]
            + [str(s.absolute()) for s in sdists]
            + ["--prefix", str(ensure_venv(path))],
            cwd=source_root / path,
            prefix="[uv pip install]",
            color_code="36",
        )
    elif are_we_editable_mode():
        pyproject = _find_development_pyproject()
        if pyproject is None:
            raise RuntimeError("No pyproject.toml found in llama-deploy-appserver")
        target = f"file://{str(pyproject.relative_to(source_root.resolve() / path, walk_up=True))}"
        run_process(
            [
                "uv",
                "pip",
                "install",
                "--reinstall",
                target,
                "--prefix",
                str(ensure_venv(path)),
            ],
            cwd=source_root / path,
            prefix="[uv pip install]",
            color_code="36",
        )
    else:
        version = _is_missing_or_outdated(path)
        if version is not None:
            if save_version:
                run_process(
                    ["uv", "add", f"llama-deploy-appserver>={version}"],
                    cwd=source_root / path,
                    prefix="[uv add]",
                    color_code="36",
                    line_transform=_exclude_venv_warning,
                )
            else:
                run_process(
                    [
                        "uv",
                        "pip",
                        "install",
                        f"llama-deploy-appserver=={version}",
                        "--prefix",
                        str(ensure_venv(path)),
                    ],
                    cwd=source_root / path,
                    prefix="[uv pip install]",
                    color_code="36",
                )


def _find_development_pyproject() -> Path | None:
    dir = Path(__file__).parent.resolve()
    while not (dir / "pyproject.toml").exists():
        dir = dir.parent
        if dir == dir.root:
            return None
    return dir


def find_python_pyproject(base: Path, config: DeploymentConfig) -> Path | None:
    path: Path | None = None
    for service_id, service_config in config.services.items():
        if service_config.python_dependencies:
            if len(service_config.python_dependencies) > 1:
                logger.warning(
                    "Llama Deploy now only supports installing from a single pyproject.toml path"
                )
            this_path = Path(service_config.python_dependencies[0])
            if path is not None and this_path != path:
                logger.warning(
                    f"Llama Deploy now only supports installing from a single pyproject.toml path, ignoring {this_path}"
                )
            else:
                path = this_path
    if path is None:
        if (base / "pyproject.toml").exists():
            path = Path(".")
    return path


def _exclude_venv_warning(line: str) -> str | None:
    if "use `--active` to target the active environment instead" in line:
        return None
    return line


def _ensure_uv_available() -> None:
    # Check if uv is available on the path
    uv_available = False
    try:
        subprocess.check_call(
            ["uv", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        uv_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    if not uv_available:
        # bootstrap uv with pip
        try:
            run_process(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "uv",
                ],
                prefix="[python -m pip]",
                color_code="31",  # red
            )
        except subprocess.CalledProcessError as e:
            msg = f"Unable to install uv. Environment must include uv, or uv must be installed with pip: {e.stderr}"
            raise RuntimeError(msg)


def _find_install_target(base: Path, config: DeploymentConfig) -> Path | None:
    return find_python_pyproject(base, config)


def _validate_path_is_safe(
    path: Path, source_root: Path, path_type: str = "path"
) -> None:
    """Validates that a path is within the source root to prevent path traversal attacks.

    Args:
        path: The path to validate
        source_root: The root directory that paths should be relative to
        path_type: Description of the path type for error messages

    Raises:
        DeploymentError: If the path is outside the source root
    """
    resolved_path = (source_root / path).resolve()
    resolved_source_root = source_root.resolve()

    if not resolved_path.is_relative_to(resolved_source_root):
        msg = (
            f"{path_type} {path} is not a subdirectory of the source root {source_root}"
        )
        raise RuntimeError(msg)


def install_ui(config: DeploymentConfig, config_parent: Path) -> None:
    if config.ui is None:
        return
    path = Path(config.ui.source.location) if config.ui.source else Path(".")
    _validate_path_is_safe(path, config_parent, "ui_source")
    run_process(
        ["pnpm", "install"],
        cwd=config_parent / path,
        prefix="[pnpm install]",
        color_code="33",
    )


def _ui_env(config: DeploymentConfig) -> dict[str, str]:
    env = os.environ.copy()
    env["LLAMA_DEPLOY_DEPLOYMENT_URL_ID"] = config.name
    env["LLAMA_DEPLOY_DEPLOYMENT_BASE_PATH"] = f"/deployments/{config.name}/ui"
    if config.ui is not None:
        env["PORT"] = str(config.ui.port)
    return env


def build_ui(config_parent: Path, config: DeploymentConfig) -> bool:
    """
    Returns True if the UI was built (and supports building), otherwise False if there's no build command
    """
    if config.ui is None:
        return False
    path = Path(config.ui.source.location) if config.ui.source else Path(".")
    _validate_path_is_safe(path, config_parent, "ui_source")
    env = _ui_env(config)

    has_build = ui_build_output_path(config_parent, config)
    if has_build is None:
        return False

    run_process(
        ["pnpm", "run", "build"],
        cwd=config_parent / path,
        env=env,
        prefix="[pnpm run build]",
        color_code="34",
    )
    return True


def start_dev_ui_process(
    root: Path, main_port: int, config: DeploymentConfig
) -> None | subprocess.Popen:
    ui = config.ui
    if ui is None:
        return None

    # If a UI dev server is already listening on the configured port, do not start another
    def _is_port_open(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            try:
                return sock.connect_ex(("127.0.0.1", port)) == 0
            except Exception:
                return False

    if _is_port_open(ui.port):
        logger.info(
            "Detected process already running on port %s; not starting a new one.",
            ui.port,
        )
        return None
    # start the ui process
    env = _ui_env(config)
    # Transform first 20 lines to replace the default UI port with the main server port
    line_counter = 0

    def _transform(line: str) -> str:
        nonlocal line_counter
        if line_counter < 20:
            line = line.replace(f":{ui.port}", f":{main_port}")
        line_counter += 1
        return line

    return spawn_process(
        ["pnpm", "run", "dev"],
        cwd=root / (ui.source.location if ui.source else "."),
        env=env,
        prefix="[pnpm run dev]",
        color_code="35",  # magenta
        line_transform=_transform,
    )
