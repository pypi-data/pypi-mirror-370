from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import SuperTuxKartClient, AsyncSuperTuxKartClient
    from xml.etree.ElementTree import Element


class Ranking:
    def __init__(self, d: Element):
        a: dict = d.attrib
        self.score: float = float(a["scores"])
        self.highest: float = float(a["max-scores"])
        self.races: int = int(a["num-races-done"])
        self.raw_score: float = float(a["raw-scores"])
        self.deviation: float = float(a["rating-deviation"])
        self._disconnects: int = int(a["disconnects"])
        self.rank = int(a["rank"])
        self.disconnect_rate: float = (
            (self._disconnects.bit_count() / min(self.races, 64) * 100)
            if self.races > 0
            else 0
        )

    def __repr__(self):
        return f"<Ranking score={self.score} highest={self.highest} races={self.races} raw_score={self.raw_score} deviation={self.deviation} rank={self.rank} disconnect_rate={self.disconnect_rate}>"


class TopPlayer(Ranking):
    def __init__(self, d: Element):
        super().__init__(d)
        self.username: str = d.attrib["username"]

    def __repr__(self):
        return f"<TopPlayer username={self.username} score={self.score} highest={self.highest} races={self.races} raw_score={self.raw_score} deviation={self.deviation} rank={self.rank} disconnect_rate={self.disconnect_rate}>"


class RankingModule:
    def __init__(self, client: SuperTuxKartClient):
        self.client: SuperTuxKartClient = client

    def get_ranking(self, id: str = None) -> Ranking:
        if not id:
            id = self.client.userid

        data = self.client.http.xml_request("/api/v2/user/get-ranking", {"id": id})
        return Ranking(data)

    def top_players(self, ntop: int = 10) -> list[TopPlayer]:

        data = self.client.http.xml_request("/api/v2/user/top-players", {"ntop": ntop})
        return [TopPlayer(x) for x in data[0]]


class AsyncRankingModule:
    def __init__(self, client: AsyncSuperTuxKartClient):
        self.client: AsyncSuperTuxKartClient = client

    async def get_ranking(self, id: str = None) -> Ranking:
        if not id:
            id = self.client.userid

        data = await self.client.http.xml_request(
            "/api/v2/user/get-ranking", {"id": id}
        )
        return Ranking(data)

    async def top_players(self, ntop: int = 10) -> list[TopPlayer]:

        data = await self.client.http.xml_request(
            "/api/v2/user/top-players", {"ntop": ntop}
        )
        return [TopPlayer(x) for x in data[0]]
