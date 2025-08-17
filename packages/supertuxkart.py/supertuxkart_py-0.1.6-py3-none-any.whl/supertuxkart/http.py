from __future__ import annotations

from . import errors
import xml.etree.ElementTree as et
from requests import Session
from aiohttp import ClientSession
import logging
from typing import TYPE_CHECKING
from urllib.parse import quote


if TYPE_CHECKING:
    from .client import SuperTuxKartClient

log = logging.getLogger("supertuxkart.http")


def raise_error(error: str):
    exc_map = {
        "Session not valid. Please sign in.": errors.InvalidSession,
        "You cannot ask yourself to be your friend!": errors.CannotFriendSelf,
        "Username required": errors.UsernameRequired,
        "Password required": errors.PasswordRequired,
        "Username or password is invalid": errors.InvalidCredentials,
    }
    raise exc_map.get(error, errors.SuperTuxKartError)(error)


def convert_payload(d: dict):
    payload = ""
    for i in d.items():
        k = str(i[0])
        v = i[1]
        if v is None:
            continue
        v = quote(str(i[1]))
        payload += f"{k}={v}&"
    return payload


class HttpClient:
    def __init__(
        self,
        client: SuperTuxKartClient,
        base_url: str = "https://online.supertuxkart.net",
        user_agent: str = "SuperTuxKart-PythonClient (https://codeberg.org/kita/stk.py)",
    ):
        self.client: SuperTuxKartClient = client
        self.base_url = base_url
        self.user_agent = user_agent
        self.session: Session = Session()

    def xml_request(
        self, endpoint: str, args: dict = {}, *, no_auth: bool = False
    ) -> et.Element:
        if not no_auth:
            if not self.client.userid or not self.client.token:
                raise RuntimeError("Initial authorization required")
            args["userid"] = self.client.userid
            args["token"] = self.client.token

        payload = convert_payload(args)

        log.debug("Sending %s to %s", payload, endpoint)
        req = self.session.post(
            self.base_url + endpoint,
            data=payload,
            headers={
                "User-Agent": self.user_agent,
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

        xml = et.fromstring(req.text)
        if xml.attrib["success"] == "no":
            return raise_error(xml.attrib["info"])

        return xml


class AsyncHttpClient:
    def __init__(
        self,
        client: SuperTuxKartClient,
        base_url: str = "https://online.supertuxkart.net",
        user_agent: str = "SuperTuxKart-PythonClient (https://codeberg.org/kita/stk.py)",
    ):
        self.client: SuperTuxKartClient = client
        self.base_url = base_url
        self.user_agent = user_agent
        self.session: ClientSession = ClientSession(
            base_url,
            headers={
                "User-Agent": self.user_agent,
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

    async def xml_request(
        self, endpoint: str, args: dict = {}, *, no_auth: bool = False
    ) -> et.Element:
        if not no_auth:
            if not self.client.userid or not self.client.token:
                raise RuntimeError("Initial authorization required")
            args["userid"] = self.client.userid
            args["token"] = self.client.token

        payload = convert_payload(args)

        log.debug("Sending %s to %s", payload, endpoint)
        req = await self.session.post(endpoint, data=payload)

        xml = et.fromstring(await req.text())
        if xml.attrib["success"] == "no":
            return raise_error(xml.attrib["info"])

        return xml
