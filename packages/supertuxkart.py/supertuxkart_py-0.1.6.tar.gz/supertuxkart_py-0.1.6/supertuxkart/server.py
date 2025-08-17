from __future__ import annotations

from ipaddress import IPv4Address, IPv6Address
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import SuperTuxKartClient, AsyncSuperTuxKartClient
    from xml.etree.ElementTree import Element
    from typing import Optional

GAME_MODES_SERVER = {
    0: "Normal Race (Grand Prix)",
    1: "Time Trial (Grand Prix)",
    3: "Normal Race",
    4: "Time Trial",
    6: "Soccer",
    7: "Free-For-All",
    8: "Capture The Flag",
}

#  In STK 2.0, it will be eventually changed:
#  Intermediate -> Casual
#  Expert -> Intermediate
#  SuperTux -> Expert
#  New SuperTux has more "harder" attributes
DIFFICULTY = {
    0: "Novice",
    1: "Intermediate",
    2: "Expert",
    3: "SuperTux",
    4: "SuperTux (STK 2.0)"
}

class ServerPlayer:
    def __init__(self, d: Element):
        a = d.attrib
        self.id: int = int(a["user-id"])
        self.username: str = a["username"]
        self.time_played: float = float(a["time-played"])
        self.country_code: Optional[str] = a.get("country-code")

        rank = a.get("rank")
        score = a.get("scores")
        max_score = a.get("max-scores")
        num_races = a.get("num-races-done")

        self.rank: Optional[int] = int(rank) if rank else None
        self.score: Optional[float] = float(score) if score else None
        self.max_score: Optional[float] = float(max_score) if max_score else None
        self.num_races: Optional[int] = int(num_races) if num_races else None

    def __eq__(self, x):
        return x == self.id

    def __repr__(self):
        return (
            f"<ServerPlayer id={self.id} "
            f"username={self.username} "
            f"time_played={self.time_played} "
            f"country_code={self.country_code} "
            f"rank={self.rank} "
            f"score={self.score} "
            f"max_score={self.max_score} "
            f"num_races={self.num_races}>"
        )


    @property
    def flag_emoji(self):
        return f"{''.join(chr(127397 + ord(str.upper(k))) for k in self.country_code)}"


class Server:
    def __init__(self, d: Element):
        s_info = d[0]
        players = d[1]

        a = s_info.attrib

        self.id: int = int(a["id"])
        self.host_id: int = int(a["host_id"])
        self.name: str = a["name"]
        self.max_players: int = int(a["max_players"])
        self.ip: IPv4Address = IPv4Address(int(a["ip"]))
        self.ipv6: Optional[IPv6Address] = (
            IPv6Address(a["ipv6"]) if a["ipv6"] != "" else None
        )
        self.port: int = int(a["port"])
        self.private_port: int = int(a["private_port"])
        self.difficulty_id: int = int(a["difficulty"])
        self.game_mode_id: int = int(a["game_mode"])
        self.current_players: int = int(a["current_players"])
        self.current_ai: int = int(a["current_ai"])
        self.password_protected: bool = bool(int(a["password"]))
        self.version: int = int(a["version"])
        self.game_started: bool = bool(int(a["game_started"]))
        self.country_code: str = a["country_code"]
        self.current_track: Optional[str] = (
            a["current_track"] if a["current_track"] != "" else None
        )
        self.distance: float = float(a["distance"])
        self.players: list[ServerPlayer] = [ServerPlayer(x) for x in players]
    
    @property
    def flag_emoji(self):
        return f"{''.join(chr(127397 + ord(str.upper(k))) for k in self.country_code)}"
    
    @property
    def game_mode(self):
        return GAME_MODES_SERVER.get(self.game_mode_id, "Unknown")
    
    @property
    def difficulty(self):
        return DIFFICULTY.get(self.difficulty_id, "Unknown")
    
    def __eq__(self, x):
        return x == self.id

    def __repr__(self):
        return (
            f"<Server name={self.name} "
            f"id={self.id} "
            f"host_id={self.host_id} "
            f"max_players={self.max_players} "
            f"ip={self.ip} "
            f"ipv6={self.ipv6} "
            f"port={self.port} "
            f"private_port={self.private_port} "
            f"difficulty_id={self.difficulty_id} "
            f"game_mode_id={self.game_mode_id} "
            f"current_players={self.current_players} "
            f"current_ai={self.current_ai} "
            f"password_protected={self.password_protected} "
            f"version={self.version} "
            f"game_started={self.game_started} "
            f"country_code={self.country_code} "
            f"current_track={self.current_track} "
            f"distance={self.distance} "
            f"players={self.players}>"
        )


class ServerModule:
    def __init__(self, client: SuperTuxKartClient):
        self.client: SuperTuxKartClient = client

    def get_all(self) -> list[Server]:
        data = self.client.http.xml_request("/api/v2/server/get-all", no_auth=True)
        return [Server(x) for x in data[0]]


class AsyncServerModule:
    def __init__(self, client: AsyncSuperTuxKartClient):
        self.client: AsyncSuperTuxKartClient = client

    async def get_all(self) -> list[Server]:
        data = await self.client.http.xml_request(
            "/api/v2/server/get-all", no_auth=True
        )
        return [Server(x) for x in data[0]]
