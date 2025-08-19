import functools

from llama_deploy.appserver.settings import BootstrapSettings, settings
from llama_deploy.core.deployment_config import DeploymentConfig


@functools.lru_cache
def get_deployment_config() -> DeploymentConfig:
    base_settings = BootstrapSettings()
    base = settings.app_root.resolve()
    yaml_file = base / settings.deployment_file_path
    name = base_settings.deployment_name
    return DeploymentConfig.from_yaml(yaml_file, name)
