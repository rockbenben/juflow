import pytest
from app.adapters.rsshub_adapter import XueqiuRsshubAdapter


@pytest.fixture
def adapter():
    return XueqiuRsshubAdapter()


def test_detect_xueqiu(adapter):
    assert adapter.detect("https://xueqiu.com/u/1234567890") is True
    assert adapter.detect("https://xueqiu.com/1234567890") is True
    assert adapter.detect("https://blog.csdn.net/test") is False


@pytest.mark.asyncio
async def test_resolve_xueqiu_with_u(adapter):
    source = await adapter.resolve("https://xueqiu.com/u/1234567890")
    assert source.platform == "xueqiu"
    assert source.platform_uid == "1234567890"
    assert source.adapter_config["rsshub_route"] == "/xueqiu/user/1234567890"


@pytest.mark.asyncio
async def test_resolve_xueqiu_without_u(adapter):
    source = await adapter.resolve("https://xueqiu.com/1234567890")
    assert source.platform_uid == "1234567890"
