import logging

from beartype.typing import Dict, Type

from .backends.bigquery import BigQueryBackend
from .backends.sqlite import SQLiteBackend
from .base import BackendBase

logger = logging.getLogger(__name__)

BACKEND_REGISTRY: Dict[str, Type[BackendBase]] = {
    "sqlite": SQLiteBackend,
    "bigquery": BigQueryBackend,
}
