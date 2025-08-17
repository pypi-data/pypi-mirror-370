from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import SuperTuxKartClient, AsyncSuperTuxKartClient
    from xml.etree.ElementTree import Element


class AddonVote:
    def __init__(self, d: Element):
        self.voted: bool = d.attrib["voted"] == "yes"
        self.rating: float = float(d.attrib["rating"])

    def __repr__(self):
        return f"<AddonVote voted={self.voted} rating={self.rating}>"


class SetAddonVote:
    def __init__(self, d: Element):
        self.new_average: float = float(d.attrib["new-average"])
        self.new_number: int = int(d.attrib["new-number"])
        self.id: str = d.attrib["addon-id"]


class AddonsModule:
    def __init__(self, client: SuperTuxKartClient):
        self.client: SuperTuxKartClient = client

    def get_addon_vote(self, id: str) -> AddonVote:
        data = self.client.http.xml_request(
            "/api/v2/user/get-addon-vote", {"addonid": id}
        )
        return AddonVote(data)

    def set_addon_vote(self, id: str, rating: int) -> SetAddonVote:
        if rating < 1 or rating > 6:
            raise ValueError("Rating must not go below 1 or above 6.")

        data = self.client.http.xml_request(
            "/api/v2/user/set-addon-vote", {"addonid": id, "rating": rating}
        )
        return SetAddonVote(data)


class AsyncAddonsModule:
    def __init__(self, client: AsyncSuperTuxKartClient):
        self.client: AsyncSuperTuxKartClient = client

    async def get_addon_vote(self, id: str) -> AddonVote:
        data = await self.client.http.xml_request(
            "/api/v2/user/get-addon-vote", {"addonid": id}
        )
        return AddonVote(data)

    async def set_addon_vote(self, id: str, rating: int) -> SetAddonVote:
        if rating < 1 or rating > 6:
            raise ValueError("Rating must not go below 1 or above 6.")

        data = await self.client.http.xml_request(
            "/api/v2/user/set-addon-vote", {"addonid": id, "rating": rating}
        )
        return SetAddonVote(data)
