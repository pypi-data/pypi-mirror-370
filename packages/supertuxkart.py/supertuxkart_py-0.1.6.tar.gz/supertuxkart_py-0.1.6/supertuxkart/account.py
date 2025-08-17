from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import SuperTuxKartClient, AsyncSuperTuxKartClient
    from xml.etree.ElementTree import Element


class SessionInfo:
    def __init__(self, data: Element):
        a = data.attrib
        self.token: str = a["token"]
        self.username: str = a["username"]
        self.realname: str = a["realname"]
        self.userid: int = int(a["userid"])
        self.achieved: list[int] | None = (
            [int(x) for x in a["achieved"].split(" ")] if a.get("achieved") else None
        )

    def __repr__(self):
        return f"<SessionInfo token={self.token} username={self.username} realname={self.realname} userid={self.userid} achieved={self.achieved}>"


class AccountsModule:
    def __init__(self, client: SuperTuxKartClient):
        self.client: SuperTuxKartClient = client

    def authorize(self) -> SessionInfo:
        if not self.client.username or not self.client.password:
            raise RuntimeError("No username and/or password specified")

        data = self.client.http.xml_request(
            "/api/v2/user/connect",
            {"username": self.client.username, "password": self.client.password},
            no_auth=True,
        )

        session = SessionInfo(data)
        self.client.userid = session.userid
        self.client.token = session.token

        return session

    def poll(self) -> None:
        self.client.http.xml_request("/api/v2/user/poll")
        return None

    def saved_session(self) -> SessionInfo:
        data = self.client.http.xml_request("/api/v2/user/saved-session")
        return SessionInfo(data)

    def client_quit(self) -> None:
        self.client.http.xml_request("/api/v2/user/client-quit")
        return None

    def disconnect(self) -> None:
        self.client.http.xml_request("/api/v2/user/disconnect")
        self.client.userid = None
        self.client.token = None
        return None

    def change_password(self, id: int = None, *, current: str, new: str) -> None:
        if not id:
            id = self.client.userid

        self.client.http.xml_request(
            "/api/v2/user/change-password",
            {"userid": id, "current": current, "new1": new, "new2": new},
            no_auth=True,
        )
        return None

    def recover(self, username: str, email: str) -> None:
        self.client.http.xml_request(
            "/api/v2/user/recover", {"username": username, "email": email}, no_auth=True
        )
        return None
    

    def register(self, username: str, password: str, email: str, real_name: str = None) -> None:
        self.client.http.xml_request(
            "/api/v2/user/register",
            {
                "username": username,
                "password": password,
                "password_confirm": password,
                "email": email,
                "realname": real_name,
                "terms": "on"
            },
            no_auth=True,
        )


class AsyncAccountsModule:
    def __init__(self, client: AsyncSuperTuxKartClient):
        self.client: AsyncSuperTuxKartClient = client

    async def authorize(self) -> SessionInfo:
        if not self.client.username or not self.client.password:
            raise RuntimeError("No username and/or password specified")

        data = await self.client.http.xml_request(
            "/api/v2/user/connect",
            {"username": self.client.username, "password": self.client.password},
            no_auth=True,
        )

        session = SessionInfo(data)
        self.client.userid = session.userid
        self.client.token = session.token

        return session

    async def poll(self) -> None:
        await self.client.http.xml_request("/api/v2/user/poll")
        return None

    async def saved_session(self) -> SessionInfo:
        data = await self.client.http.xml_request("/api/v2/user/saved-session")
        return SessionInfo(data)

    async def client_quit(self) -> None:
        await self.client.http.xml_request("/api/v2/user/client-quit")
        return None

    async def disconnect(self) -> None:
        await self.client.http.xml_request("/api/v2/user/disconnect")
        self.client.userid = None
        self.client.token = None
        return None

    async def change_password(self, id: int = None, *, current: str, new: str) -> None:
        if not id:
            id = self.client.userid

        await self.client.http.xml_request(
            "/api/v2/user/change-password",
            {"userid": id, "current": current, "new1": new, "new2": new},
            no_auth=True,
        )
        return None

    async def recover(self, username: str, email: str) -> None:
        await self.client.http.xml_request(
            "/api/v2/user/recover", {"username": username, "email": email}, no_auth=True
        )
        return None


    async def register(self, username: str, password: str, email: str, real_name: str = None) -> None:
        await self.client.http.xml_request(
            "/api/v2/user/register",
            {
                "username": username,
                "password": password,
                "password_confirm": password,
                "email": email,
                "realname": real_name,
                "terms": "on"
            },
            no_auth=True,
        )

