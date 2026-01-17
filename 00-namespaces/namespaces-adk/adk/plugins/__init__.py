"""
Plugins: Plugin system for extensibility.

This package provides plugin infrastructure for tools, memory,
workflows, and SDK integrations.
"""

from ..core.plugin_manager import (
    Plugin,
    PluginInterface,
    PluginManager,
    PluginManifest,
    PluginType,
)

__all__ = [
    "PluginManager",
    "Plugin",
    "PluginManifest",
    "PluginType",
    "PluginInterface",
]
