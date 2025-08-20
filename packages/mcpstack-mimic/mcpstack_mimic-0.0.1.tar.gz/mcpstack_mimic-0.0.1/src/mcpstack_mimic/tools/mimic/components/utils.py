import logging
from pathlib import Path

import yaml
from beartype import beartype
from beartype.typing import Any, Dict
from MCPStack.core.config import StackConfig

logger = logging.getLogger(__name__)

CONFIG_DIR = Path(__file__).parent.parent / "configurations"


@beartype
def load_supported_datasets() -> Dict[str, Dict[str, Any]]:
    yaml_path = CONFIG_DIR / "datasets.yaml"
    if not yaml_path.exists():
        raise RuntimeError(f"datasets.yaml not found at {yaml_path}")
    with open(yaml_path) as f:
        return yaml.safe_load(f)


@beartype
def get_dataset_config(dataset_name: str) -> Dict[str, Any] | None:
    datasets = load_supported_datasets()
    return datasets.get(dataset_name.lower())


@beartype
def get_default_database_path(
    config: StackConfig, dataset_name: str | None = None
) -> Path:
    data_dir = config.data_dir
    if dataset_name:
        ds_cfg = get_dataset_config(dataset_name)
        if ds_cfg and ds_cfg.get("default_db_filename"):
            return data_dir / ds_cfg["default_db_filename"]
        # If dataset provided but no filename in YAML, mirror its name
        return data_dir / f"{dataset_name.replace('-', '_')}.db"
    return data_dir / "mimic.sqlite"


@beartype
def get_dataset_raw_files_path(config: StackConfig, dataset_name: str) -> Path:
    path = config.raw_files_dir / dataset_name.lower()
    path.mkdir(parents=True, exist_ok=True)
    return path


@beartype
def load_security_config() -> Dict[str, Any]:
    yaml_path = CONFIG_DIR / "security.yaml"
    if not yaml_path.exists():
        raise RuntimeError(f"security.yaml not found at {yaml_path}")
    with open(yaml_path) as f:
        return yaml.safe_load(f)


@beartype
def load_env_vars_config() -> Dict[str, Any]:
    yaml_path = CONFIG_DIR / "env_vars.yaml"
    if not yaml_path.exists():
        raise RuntimeError(f"env_vars.yaml not found at {yaml_path}")
    with open(yaml_path) as f:
        return yaml.safe_load(f)


@beartype
def validate_limit(value: int) -> bool:
    return isinstance(value, int) and 1 <= value <= 1000
