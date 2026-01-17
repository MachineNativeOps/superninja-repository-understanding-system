"""
Schema System - INSTANT 執行標準

整合所有 Schema 系統組件
"""

from .compatibility_checker import CompatibilityChecker, CompatibilityStatus
from .schema_registry import SchemaEntry, SchemaRegistry
from .schema_versioning import SchemaVersioning, VersionChange, VersionChangeType

__all__ = [
    "SchemaRegistry",
    "SchemaEntry",
    "SchemaVersioning",
    "VersionChange",
    "VersionChangeType",
    "CompatibilityChecker",
    "CompatibilityStatus",
]
