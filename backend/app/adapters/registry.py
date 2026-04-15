from app.adapters.base import BaseAdapter


class AdapterRegistry:
    def __init__(self):
        self._adapters: list[BaseAdapter] = []

    _priority = {"rss": 0, "rsshub": 1, "scraper": 2}

    def register(self, adapter: BaseAdapter) -> None:
        self._adapters.append(adapter)

    def detect(self, url: str) -> BaseAdapter | None:
        for adapter in self._adapters:
            if adapter.detect(url):
                return adapter
        return None

    def get_by_platform(self, platform: str) -> BaseAdapter | None:
        for adapter in self._adapters:
            if adapter.platform == platform:
                return adapter
        return None

    def get_adapters_by_platform(self, platform: str) -> list[BaseAdapter]:
        """Return all adapters for a platform, sorted by priority (rss > rsshub > scraper)."""
        adapters = [a for a in self._adapters if a.platform == platform]
        return sorted(adapters, key=lambda a: self._priority.get(a.adapter_type, 99))

    def unregister(self, platform: str, adapter_type: str | None = None) -> None:
        self._adapters = [a for a in self._adapters
            if not (a.platform == platform and (adapter_type is None or a.adapter_type == adapter_type))]

    @property
    def platforms(self) -> list[str]:
        return [a.platform for a in self._adapters]


registry = AdapterRegistry()
