import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from app.adapters.base import BaseAdapter
from app.adapters.registry import registry


@dataclass
class PluginInfo:
    name: str
    display_name: str
    version: str
    author: str
    description: str
    adapter_class: str
    url_patterns: list[str]
    path: str


class PluginLoader:
    def __init__(self, plugins_dir: str = "plugins/adapters"):
        self.plugins_dir = Path(plugins_dir)
        self._loaded: dict[str, BaseAdapter] = {}

    def scan_plugins(self) -> list[PluginInfo]:
        plugins = []
        if not self.plugins_dir.exists():
            return plugins
        for entry in self.plugins_dir.iterdir():
            if not entry.is_dir():
                continue
            manifest_path = entry / "manifest.json"
            if not manifest_path.exists():
                continue
            with open(manifest_path) as f:
                manifest = json.load(f)
            plugins.append(PluginInfo(
                name=manifest["name"],
                display_name=manifest.get("display_name", manifest["name"]),
                version=manifest.get("version", "0.0.0"),
                author=manifest.get("author", ""),
                description=manifest.get("description", ""),
                adapter_class=manifest["adapter_class"],
                url_patterns=manifest.get("url_patterns", []),
                path=str(entry),
            ))
        return plugins

    def load_plugin(self, plugin_dir: str) -> BaseAdapter | None:
        plugin_path = Path(plugin_dir)
        manifest_path = plugin_path / "manifest.json"
        adapter_path = plugin_path / "adapter.py"
        if not manifest_path.exists() or not adapter_path.exists():
            return None
        with open(manifest_path) as f:
            manifest = json.load(f)
        module_name = f"juflow_plugin_{manifest['name']}"
        spec = importlib.util.spec_from_file_location(module_name, str(adapter_path))
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        adapter_cls = getattr(module, manifest["adapter_class"])
        adapter = adapter_cls()
        registry.register(adapter)
        self._loaded[manifest["name"]] = adapter
        return adapter

    def unload_plugin(self, plugin_name: str) -> bool:
        adapter = self._loaded.pop(plugin_name, None)
        if adapter:
            registry.unregister(adapter.platform, adapter.adapter_type)
            sys.modules.pop(f"juflow_plugin_{plugin_name}", None)
            return True
        return False

    def load_all_enabled(self, enabled_names: list[str]) -> int:
        count = 0
        for info in self.scan_plugins():
            if info.name in enabled_names:
                if self.load_plugin(info.path):
                    count += 1
        return count


plugin_loader = PluginLoader()
