import pytest

from app.adapters.base import BaseAdapter, SourceInfo, ArticleItem
from app.adapters.registry import AdapterRegistry


class FakeAdapter(BaseAdapter):
    platform = "fake"
    name = "Fake Platform"
    adapter_type = "rss"

    def detect(self, url: str) -> bool:
        return "fake.com" in url

    async def resolve(self, url: str) -> SourceInfo:
        return SourceInfo(platform="fake", platform_uid="123", display_name="Fake User", home_url=url)

    async def fetch(self, source: SourceInfo, cookies=None) -> list[ArticleItem]:
        return [ArticleItem(title="Test", url="https://fake.com/1")]


def test_register_and_detect():
    reg = AdapterRegistry()
    adapter = FakeAdapter()
    reg.register(adapter)
    assert reg.detect("https://fake.com/user/123") is adapter
    assert reg.detect("https://other.com/user") is None


def test_get_by_platform():
    reg = AdapterRegistry()
    adapter = FakeAdapter()
    reg.register(adapter)
    assert reg.get_by_platform("fake") is adapter
    assert reg.get_by_platform("unknown") is None


def test_platforms_list():
    reg = AdapterRegistry()
    reg.register(FakeAdapter())
    assert reg.platforms == ["fake"]
