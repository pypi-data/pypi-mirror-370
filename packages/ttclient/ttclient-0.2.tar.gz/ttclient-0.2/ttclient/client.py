from dataclasses import fields
from typing import cast

from .abc import Chat, TeamData, UserData
from .base import BaseClient


def factory[T](dataclass: type[T], data: dict) -> T:
    _fields = set(f.name for f in fields(Chat)) & set(data.keys())
    return dataclass(**{field: data[field] for field in _fields})


class TTClient(BaseClient):
    async def send_post(self, chat_id: int, text: str) -> None:
        await self.post('/bot/message', chat_id=chat_id, text=text)

    async def send_private_post(self, user_id: int, text: str) -> None:
        await self.post('/msg/post/private', user_id=user_id, text=text)

    async def get_user_data(self, ids: list[int]) -> list[UserData]:
        data = await self.get('/user/list', ids=','.join(map(str, ids)))
        return cast(list[UserData], data['users'])

    async def get_team_data(self, ids: list[int]) -> list[TeamData]:
        data = await self.get('/core/org', ids=','.join(map(str, ids)))
        return cast(list[TeamData], data['orgs'])

    async def get_chat_data(self, ids: list[int]) -> list[dict]:
        data = await self.get('/core/chat', ids=','.join(map(str, ids)))
        return cast(list[dict], data['chats'])

    async def get_chat(self, chat_id: int) -> Chat:
        data = await self.get('/core/chat', ids=chat_id)
        return factory(Chat, data['chats'][0])
