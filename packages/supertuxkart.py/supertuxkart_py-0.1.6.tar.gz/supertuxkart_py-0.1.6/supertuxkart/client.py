import logging

from .http import HttpClient, AsyncHttpClient
from .account import AccountsModule, AsyncAccountsModule
from .users import UsersModule, AsyncUsersModule
from .relationships import RelationshipsModule, AsyncRelationshipsModule
from .addons import AddonsModule, AsyncAddonsModule
from .ranking import RankingModule, AsyncRankingModule
from .server import ServerModule, AsyncServerModule


class SuperTuxKartClient:
    def __init__(
        self,
        *,
        userid: int = None,
        token: str = None,
        username: str = None,
        password: str = None,
        base_url="https://online.supertuxkart.net",
    ):
        self.username = username
        self.password = password
        self.userid = userid
        self.token = token
        self.http = HttpClient(self, base_url)
        self.account = AccountsModule(self)
        self.users = UsersModule(self)
        self.relationships = RelationshipsModule(self)
        self.addons = AddonsModule(self)
        self.ranking = RankingModule(self)
        self.server = ServerModule(self)


class AsyncSuperTuxKartClient:
    def __init__(
        self,
        *,
        userid: int = None,
        token: str = None,
        username: str = None,
        password: str = None,
        base_url="https://online.supertuxkart.net",
    ):
        self.username = username
        self.password = password
        self.userid = userid
        self.token = token
        self.http = AsyncHttpClient(self, base_url)
        self.account = AsyncAccountsModule(self)
        self.users = AsyncUsersModule(self)
        self.relationships = AsyncRelationshipsModule(self)
        self.addons = AsyncAddonsModule(self)
        self.ranking = AsyncRankingModule(self)
        self.server = AsyncServerModule(self)
