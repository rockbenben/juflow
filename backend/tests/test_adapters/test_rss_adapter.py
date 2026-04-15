import pytest
from app.adapters.rss_adapter import CsdnRssAdapter, ZhihuRssAdapter


@pytest.fixture
def csdn():
    return CsdnRssAdapter()


@pytest.fixture
def zhihu():
    return ZhihuRssAdapter()


def test_detect_csdn(csdn):
    assert csdn.detect("https://blog.csdn.net/username") is True
    assert csdn.detect("https://blog.csdn.net/username/article/details/123") is True
    assert csdn.detect("https://www.zhihu.com/people/test") is False


@pytest.mark.asyncio
async def test_resolve_csdn(csdn):
    source = await csdn.resolve("https://blog.csdn.net/test_user/article/details/123")
    assert source.platform == "csdn"
    assert source.platform_uid == "test_user"
    assert source.adapter_config["rss_url"] == "https://blog.csdn.net/test_user/rss/list"


def test_detect_zhihu(zhihu):
    assert zhihu.detect("https://www.zhihu.com/people/someone") is True
    assert zhihu.detect("https://zhihu.com/column/my-column") is True
    assert zhihu.detect("https://blog.csdn.net/user") is False


@pytest.mark.asyncio
async def test_resolve_zhihu_people(zhihu):
    source = await zhihu.resolve("https://www.zhihu.com/people/someone")
    assert source.platform == "zhihu"
    assert source.platform_uid == "someone"
    assert source.adapter_config["is_column"] is False


@pytest.mark.asyncio
async def test_resolve_zhihu_column(zhihu):
    source = await zhihu.resolve("https://zhihu.com/column/my-column")
    assert source.platform_uid == "my-column"
    assert source.adapter_config["is_column"] is True
    assert "column/my-column/rss" in source.adapter_config["rss_url"]
