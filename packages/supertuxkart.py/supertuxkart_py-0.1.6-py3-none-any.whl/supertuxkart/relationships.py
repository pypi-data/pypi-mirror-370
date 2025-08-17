from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .client import SuperTuxKartClient, AsyncSuperTuxKartClient
    from xml.etree.ElementTree import Element


class Friend:
    def __init__(self, data: Element):
        fprops = data.attrib
        self.id: int = int(data[0].attrib["id"])
        self.username: str = data[0].attrib["user_name"]
        self.is_pending: bool = fprops.get("is_pending") == "yes"
        self.is_asker: bool = fprops.get("is_asker") == "yes"
        self.online: bool = fprops.get("online") == "yes"
        self.date: datetime | None = None
        if date := fprops.get("date"):
            self.date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    
    def __eq__(self, x):
        return x == self.id

    def __repr__(self):
        return f"<Friend id={self.id} username={self.username} is_pending={self.is_pending} online={self.online} date={repr(self.date)}>"


class RelationshipsModule:
    def __init__(self, client: SuperTuxKartClient):
        self.client: SuperTuxKartClient = client

    def friend_request(self, id: int):
        self.client.http.xml_request("/api/v2/user/friend-request", {"friendid": id})
        return None

    def accept_friend_request(self, id: int):
        self.client.http.xml_request(
            "/api/v2/user/accept-friend-request", {"friendid": id}
        )
        return None

    def decline_friend_request(self, id: int):
        self.client.http.xml_request(
            "/api/v2/user/decline-friend-request", {"friendid": id}
        )
        return None

    def cancel_friend_request(self, id: int):
        self.client.http.xml_request(
            "/api/v2/user/cancel-friend-request", {"friendid": id}
        )
        return None

    def remove_friend(self, id: int):
        self.client.http.xml_request("/api/v2/user/remove-friend", {"friendid": id})
        return None

    def get_friends_list(self, id: int = None):
        if not id:
            id = self.client.userid

        res = []

        data = self.client.http.xml_request(
            "/api/v2/user/get-friends-list", {"visitingid": id}
        )
        friend_elements = data[0].findall("friend")
        for f in friend_elements:
            res.append(Friend(f))

        return res


class AsyncRelationshipsModule:
    def __init__(self, client: AsyncSuperTuxKartClient):
        self.client: AsyncSuperTuxKartClient = client

    async def friend_request(self, id: int):
        await self.client.http.xml_request(
            "/api/v2/user/friend-request", {"friendid": id}
        )
        return None

    async def accept_friend_request(self, id: int):
        await self.client.http.xml_request(
            "/api/v2/user/accept-friend-request", {"friendid": id}
        )
        return None

    async def decline_friend_request(self, id: int):
        await self.client.http.xml_request(
            "/api/v2/user/decline-friend-request", {"friendid": id}
        )
        return None

    async def cancel_friend_request(self, id: int):
        self.client.http.xml_request(
            "/api/v2/user/cancel-friend-request", {"friendid": id}
        )
        return None

    async def remove_friend(self, id: int):
        await self.client.http.xml_request(
            "/api/v2/user/remove-friend", {"friendid": id}
        )
        return None

    async def get_friends_list(self, id: int = None):
        if not id:
            id = self.client.userid

        res = []

        data = await self.client.http.xml_request(
            "/api/v2/user/get-friends-list", {"visitingid": id}
        )
        friend_elements = data[0].findall("friend")
        for f in friend_elements:
            res.append(Friend(f))

        return res
