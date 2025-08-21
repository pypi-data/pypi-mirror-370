import pytest


@pytest.mark.asyncio(scope='session')
async def test_endpoint_test_async_igvf_api():
    from igvf_async_client import AsyncIgvfApi
    api = AsyncIgvfApi()
    result = await api.search(query='ABC')
    assert result.total > 2
    result = await api.search(query='ABC', type=['Software'])
    assert result.graph[0].actual_instance.type == ['Software', 'Item']


@pytest.mark.asyncio(scope='session')
async def test_endpoints_test_search_field_filters():
    from igvf_async_client import AsyncIgvfApi
    api = AsyncIgvfApi()
    r = await api.search(type=['Item'], field_filters={'status': 'current'})
    assert r.total > 100
    r2 = await api.search(type=['Item'], field_filters={'status': ['current', 'released']})
    assert r2.total > r.total
