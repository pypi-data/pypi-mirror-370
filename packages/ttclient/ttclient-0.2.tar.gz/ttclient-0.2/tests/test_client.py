from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from ttclient import TTClient


@pytest.fixture(scope='module')
def client():
    return TTClient('123', host='localhost')


class HttpClient:
    result = AsyncMock()

    def __init__(self, *args, **kwargs):
        assert kwargs.get('headers', {}) == {'X-APIToken': '123'}

    async def __aenter__(self):
        return MagicMock(request=self.result)

    async def __aexit__(self, exc_type, exc, tb):
        pass


async def test_repr_ok(client):
    assert str(client) == 'Client [https://localhost] with secret'


async def test_send_post_ok(client, monkeypatch):
    class HttpClient1(HttpClient):
        result = AsyncMock(return_value=MagicMock(status_code=200, json=lambda: {}))

    monkeypatch.setattr(httpx, 'AsyncClient', HttpClient1)

    assert not await client.send_post(1, 'text')

    HttpClient1.result.assert_called_once_with('POST', 'https://localhost/bot/message',
        json={'chat_id': 1, 'text': 'text'})


async def test_send_private_post_ok(client, monkeypatch):
    class HttpClient1(HttpClient):
        result = AsyncMock(return_value=MagicMock(status_code=200, json=lambda: {}))

    monkeypatch.setattr(httpx, 'AsyncClient', HttpClient1)

    assert not await client.send_private_post(1, 'text')

    HttpClient1.result.assert_called_once_with('POST', 'https://localhost/msg/post/private',
        json={'user_id': 1, 'text': 'text'})
