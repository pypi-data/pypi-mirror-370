from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import SuperTuxKartClient, AsyncSuperTuxKartClient
    from xml.etree.ElementTree import Element


class User:
    def __init__(self, d: Element):
        self.id: int = int(d.attrib["id"])
        self.username: str = d.attrib["user_name"]
    
    def __eq__(self, x):
        return x == self.id

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"


class UsersModule:
    def __init__(self, client: SuperTuxKartClient):
        self.client: SuperTuxKartClient = client

    def get_achievements(self, visiting_id: int = None):
        data = self.client.http.xml_request(
            "/api/v2/user/get-achievements", {"visitingid": visiting_id}
        )
        return [int(x) for x in data.attrib["achieved"].split(" ")]

    def user_search(self, query: str) -> list[User]:
        data = self.client.http.xml_request(
            "/api/v2/user/user-search", {"search-string": query}
        )

        return [User(x) for x in data[0].findall("user")]


class AsyncUsersModule:
    def __init__(self, client: AsyncSuperTuxKartClient):
        self.client: AsyncSuperTuxKartClient = client

    async def get_achievements(self, visiting_id: int = None):
        data = await self.client.http.xml_request(
            "/api/v2/user/get-achievements", {"visitingid": visiting_id}
        )
        return [int(x) for x in data.attrib["achieved"].split(" ")]

    async def user_search(self, query: str) -> list[User]:
        data = await self.client.http.xml_request(
            "/api/v2/user/user-search", {"search-string": query}
        )

        return [User(x) for x in data[0].findall("user")]
