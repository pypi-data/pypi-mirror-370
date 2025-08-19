from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from ttclient.base import (BaseClient, InputDataError, MethodError,
                           NoAccessError, NotFoundError, RedirectError,
                           ServerError, TooManyRequestsError,
                           UnauthorizedError)


@pytest.fixture
def client():
    return BaseClient('1234567890qwertyuasdfgxcvbnwert', host='localhost')


async def test_api_call_ok_repr(client):
    assert repr(client) == 'Client [https://localhost] with secret'


async def test_api_call_ok(client, monkeypatch):
    request_mock = AsyncMock(return_value=MagicMock(status_code=200, json=lambda: {'data': []}))
    monkeypatch.setattr(httpx.AsyncClient, 'request', request_mock)

    assert await client.api_call('GET', '/core/chat', ids=1) == {'data': []}
    request_mock.assert_called_once_with('GET', 'https://localhost/core/chat', params={'ids': 1})

    assert await client.api_call('GET', '/core/chat') == {'data': []}
    request_mock.assert_called_with('GET', 'https://localhost/core/chat', params={})

    assert await client.api_call('DELETE', '/core/chat/1') == {'data': []}
    request_mock.assert_called_with('DELETE', 'https://localhost/core/chat/1', params={})

    assert await client.api_call('POST', '/core/chat') == {'data': []}
    request_mock.assert_called_with('POST', 'https://localhost/core/chat', json={})

    assert await client.api_call('POST', '/core/chat', title='title') == {'data': []}
    request_mock.assert_called_with('POST', 'https://localhost/core/chat', json={'title': 'title'})

    assert await client.api_call('PUT', '/core/chat/1', title='title') == {'data': []}
    request_mock.assert_called_with('PUT', 'https://localhost/core/chat/1', json={'title': 'title'})


async def test_call_ok(client):
    client.api_call = AsyncMock(return_value={})
    assert await client('GET', '/core/chat', ids=1) == {}
    client.api_call.assert_called_once_with('GET', '/core/chat', ids=1)

    client.api_call = AsyncMock(return_value={})
    assert await client('PUT', '/core/chat/{}', 2, ids=1) == {}
    client.api_call.assert_called_once_with('PUT', '/core/chat/2', ids=1)


async def test_get_ok(client):
    client.api_call = AsyncMock(return_value={})
    assert await client.get('/core/chat', ids=1) == {}
    client.api_call.assert_called_once_with('GET', '/core/chat', ids=1)


async def test_post_ok(client):
    client.api_call = AsyncMock(return_value={})
    assert await client.post('/core/chat', ids=1) == {}
    client.api_call.assert_called_once_with('POST', '/core/chat', ids=1)


async def test_put_ok(client):
    client.api_call = AsyncMock(return_value={})
    assert await client.put('/core/chat', ids=1) == {}
    client.api_call.assert_called_once_with('PUT', '/core/chat', ids=1)


async def test_delete_ok(client):
    client.api_call = AsyncMock(return_value={})
    assert await client.delete('/core/chat', ids=1) == {}
    client.api_call.assert_called_once_with('DELETE', '/core/chat', ids=1)


async def test_api_call_err_400(client, monkeypatch):
    request_mock = AsyncMock(return_value=MagicMock(status_code=400, json=lambda: {'data': []}))
    monkeypatch.setattr(httpx.AsyncClient, 'request', request_mock)

    with pytest.raises(InputDataError) as err:
        await client.api_call('GET', '/core/chat', ids=1)

    assert err.value.method == 'GET'
    assert err.value.uri == '/core/chat'
    assert err.value.data == {'ids': 1}
    assert err.value.result == {'data': []}
    assert err.value.status_code == 400
    assert err.value.args[0] == "GET /core/chat \n<- {'ids': 1} \n-> {'data': []}"

    request_mock.assert_called_once_with('GET', 'https://localhost/core/chat', params={'ids': 1})


async def test_api_call_err_401(client, monkeypatch):
    request_mock = AsyncMock(return_value=MagicMock(status_code=401, json=dict))
    monkeypatch.setattr(httpx.AsyncClient, 'request', request_mock)

    with pytest.raises(UnauthorizedError) as err:
        await client.api_call('GET', '/core/chat')

    assert err.value.status_code == 401
    assert err.value.args[0] == 'GET /core/chat \n-> {}'
    request_mock.assert_called_once_with('GET', 'https://localhost/core/chat', params={})


async def test_api_call_err_403(client, monkeypatch):
    request_mock = AsyncMock(return_value=MagicMock(status_code=403, json=dict))
    monkeypatch.setattr(httpx.AsyncClient, 'request', request_mock)

    with pytest.raises(NoAccessError) as err:
        await client.api_call('GET', '/core/chat')

    assert err.value.status_code == 403
    assert err.value.args[0] == 'GET /core/chat \n<- {} \n-> {}'
    request_mock.assert_called_once_with('GET', 'https://localhost/core/chat', params={})


async def test_api_call_err_404(client, monkeypatch):
    request_mock = AsyncMock(return_value=MagicMock(status_code=404, json=dict))
    monkeypatch.setattr(httpx.AsyncClient, 'request', request_mock)

    with pytest.raises(NotFoundError) as err:
        await client.api_call('GET', '/core/chat')

    assert err.value.status_code == 404
    assert err.value.args[0] == 'NotFound /core/chat'
    request_mock.assert_called_once_with('GET', 'https://localhost/core/chat', params={})


async def test_api_call_err_405(client, monkeypatch):
    request_mock = AsyncMock(return_value=MagicMock(status_code=405, json=dict))
    monkeypatch.setattr(httpx.AsyncClient, 'request', request_mock)

    with pytest.raises(MethodError) as err:
        await client.api_call('GET', '/core/chat')

    assert err.value.status_code == 405
    assert err.value.args[0] == 'GET undefined for /core/chat'
    request_mock.assert_called_once_with('GET', 'https://localhost/core/chat', params={})


async def test_api_call_err_429(client, monkeypatch):
    request_mock = AsyncMock(return_value=MagicMock(status_code=429, json=dict))
    monkeypatch.setattr(httpx.AsyncClient, 'request', request_mock)

    with pytest.raises(TooManyRequestsError) as err:
        await client.api_call('GET', '/core/chat')

    assert err.value.status_code == 429
    assert err.value.args[0] == 'GET /core/chat\n-> {}'
    request_mock.assert_called_once_with('GET', 'https://localhost/core/chat', params={})


async def test_api_call_err_301(client, monkeypatch):
    request_mock = AsyncMock(return_value=MagicMock(status_code=301, json=dict))
    monkeypatch.setattr(httpx.AsyncClient, 'request', request_mock)

    with pytest.raises(RedirectError) as err:
        await client.api_call('GET', '/core/chat')

    assert err.value.status_code == 301
    assert err.value.args[0] == 'GET /core/chat'
    request_mock.assert_called_once_with('GET', 'https://localhost/core/chat', params={})


async def test_api_call_err_302(client, monkeypatch):
    request_mock = AsyncMock(return_value=MagicMock(status_code=302, json=dict))
    monkeypatch.setattr(httpx.AsyncClient, 'request', request_mock)

    with pytest.raises(RedirectError) as err:
        await client.api_call('GET', '/core/chat')

    assert err.value.status_code == 302
    assert err.value.args[0] == 'GET /core/chat'
    request_mock.assert_called_once_with('GET', 'https://localhost/core/chat', params={})


async def test_api_call_err_500(client, monkeypatch):
    request_mock = AsyncMock(return_value=MagicMock(status_code=500, json=dict))
    monkeypatch.setattr(httpx.AsyncClient, 'request', request_mock)

    with pytest.raises(ServerError) as err:
        await client.api_call('GET', '/core/chat')

    assert err.value.status_code == 500
    assert err.value.args[0] == 'GET /core/chat > HTTP500'
    request_mock.assert_called_once_with('GET', 'https://localhost/core/chat', params={})


async def test_api_call_err_502(client, monkeypatch):
    request_mock = AsyncMock(return_value=MagicMock(status_code=502, json=dict))
    monkeypatch.setattr(httpx.AsyncClient, 'request', request_mock)

    with pytest.raises(ServerError) as err:
        await client.api_call('GET', '/core/chat')

    assert err.value.status_code == 502
    assert err.value.args[0] == 'GET /core/chat > HTTP502'
    request_mock.assert_called_once_with('GET', 'https://localhost/core/chat', params={})


async def test_api_call_err_503(client, monkeypatch):
    request_mock = AsyncMock(return_value=MagicMock(status_code=503, json=dict))
    monkeypatch.setattr(httpx.AsyncClient, 'request', request_mock)

    with pytest.raises(ServerError) as err:
        await client.api_call('GET', '/core/chat')

    assert err.value.status_code == 503
    assert err.value.args[0] == 'GET /core/chat > HTTP503'
    request_mock.assert_called_once_with('GET', 'https://localhost/core/chat', params={})


async def test_api_call_err_504(client, monkeypatch):
    request_mock = AsyncMock(return_value=MagicMock(status_code=504, json=dict))
    monkeypatch.setattr(httpx.AsyncClient, 'request', request_mock)

    with pytest.raises(ServerError) as err:
        await client.api_call('GET', '/core/chat')

    assert err.value.status_code == 504
    assert err.value.args[0] == 'GET /core/chat > HTTP504'
    request_mock.assert_called_once_with('GET', 'https://localhost/core/chat', params={})
