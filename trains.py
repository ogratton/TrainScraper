"""
Scrapes www.opentraintimes.com for the trains coming past my house

This site gets its data from https://datafeeds.networkrail.co.uk,
but where's the fun in that?

Site uses socket.io protocol
https://socket.io/docs/internals
https://github.com/socketio/engine.io-protocol

TODO:
    - use threading/gevent
    - add in approx time from berth
    - add overground berths
    - scrape train journey name too
        - it's just /schedule/{train_name}/{date}
        but should wait for async
"""
from __future__ import annotations
from .yeast import yeast

from dataclasses import dataclass
from typing import Iterator
from typing import List
from typing import Union
from typing import Tuple
from typing import Optional
from requests import Session
from time import sleep

import logging
import json
import re

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

Message = List[Union[str, dict]]


class SessionExpired(Exception):
    ...


@dataclass
class WebsocketPoller:
    """
    Poll the websocket over standard xhr polling, instead
    of using websocket-client. This was found to be
    the easiest and most consistent method.
    """
    local_map: str

    _base_url = "www.opentraintimes.com/socket.io/"
    _re_extract_handshake = re.compile(r"({.*})")
    _re_extract_messages = re.compile(r"42(\[.*?\])(?=\\x|$)?")

    def connect(self, session: Session, consumer: MessageConsumer, retries=3):
        if not retries:
            raise RuntimeError("Can't connect")
        try:
            handshake = self._connect(session)
        except SessionExpired:
            # Just try again
            return self.connect(session, consumer, retries-1)
        sid = handshake['sid']
        post_message = self._generate_post_message(self.local_map)
        self._post_map(session, sid, post_message)
        self._poll(session, sid, handshake['pingInterval'], consumer)

    def _poll(self, session: Session, sid, ping_interval, consumer: MessageConsumer):
        heartbeat_freq = (ping_interval / 1000)
        counter = 0
        while True:
            try:
                messages = self._poll_messages(session, sid)
            except SessionExpired:
                logger.warning("DISCONNECTED - attempting to reconnect")
                return self.connect(session, consumer)
            # print("Deserialised: %s", messages)
            res = list(consumer.parse_message_list(messages))  # TODO shouldn't be done here
            if res:
                print(f"RES: {list(res)}")

            sleep(1)
            counter += 1
            if counter % heartbeat_freq == 0:
                # TODO it's not really every 5 seconds if requests block
                #   That's why it loses connection sometimes
                self._send_heartbeat(session, sid)

    @classmethod
    def _connect(cls, session: Session):
        handshake = cls._poll_handshake(session)
        _version = cls._poll_messages(session, handshake['sid'])
        return handshake

    @classmethod
    def _poll_handshake(cls, session: Session) -> dict:
        poll_response = cls._poll_xhr(session)
        json_dict = cls._extract_handshake(poll_response)
        logger.debug(f"> handshake: {json_dict}")
        return json_dict

    @classmethod
    def _poll_messages(cls, session: Session, sid: str) -> List[Message]:
        poll_response = cls._poll_xhr(session, sid)
        messages = cls._extract_messages(poll_response)
        logger.debug(f"> messages: {messages}")
        return messages

    @classmethod
    def _poll_xhr(cls, session: Session, sid=None) -> bytes:
        t_val = yeast()
        sid_arg = f"&sid={sid}" if sid else ""
        url = f"https://{cls._base_url}?EIO=3&transport=polling&t={t_val}{sid_arg}"
        page = session.get(url)
        logger.debug(f"URL: {url}")
        logger.debug(f"PAGE: {page.content}")
        return page.content

    @classmethod
    def _generate_post_message(cls, local_map: str):
        template = f'42["join","{local_map}"]'
        return f"{len(template)}:{template}"

    @classmethod
    def _post_map(cls, session: Session, sid: str, message: str):
        t_val = yeast()
        url = f"https://{cls._base_url}?EIO=3&transport=polling&t={t_val}&sid={sid}"
        print("Heartbeat")
        logger.debug(f"POST: {url}")
        page = session.post(url, data=message)
        logger.debug(f"> post: {page.content}",)

    @classmethod
    def _send_heartbeat(cls, session, sid):
        cls._post_map(session, sid, "1:2")
        # TODO can sometimes be an actual message instead of a pong...
        # pong = cls._poll_xhr(session, sid)
        # logger.debug(f"PONG: {pong}")

    @classmethod
    def _extract_handshake(cls, b: bytes) -> dict:
        """
        v lazy but it works
        """
        json_str = cls._re_extract_handshake.search(str(b)).group(1)
        return json.loads(json_str)

    @classmethod
    def _extract_messages(cls, b: bytes) -> List[Message]:
        if b"Session ID unknown" in b:
            raise SessionExpired
        json_strs = cls._re_extract_messages.findall(str(b))
        return [json.loads(json_str) for json_str in json_strs]


@dataclass
class MessageConsumer:
    """
    Example message:
    42["OTT.MAP.lec1",{"e":"WJ0139","a":{"t":"BTH","uid":"C73090","date":"2020-02-22","descr":"1S69"}}]
    means train C73090 is at berth WJ0139
    """
    interesting_berths: List[str]
    expected_map: str

    def parse_message_list(self, messages: List[Message]) -> Iterator[Tuple[str, str]]:
        """
        Shout if there's a train at a berth we're 'subscribed' to 
        """
        for message in messages:
            # print(f"MESSAGE: {message}")
            if res := self._parse_message(message):
                yield res
    
    def _parse_message(self, message: Message) -> Optional[Tuple[str, str]]:
        if not message:
            return None
        map_name, info = message
        if self.expected_map not in map_name:
            logger.warning("Don't understand this message: %s", message)
            return None
        if not info:
            return None

        berth = info.get("e")
        berth_info = info.get("a")
        if not berth_info:
            return None
        train = berth_info.get("uid")

        logger.debug("PARSED TRAIN: %s at %s", train, berth)
        
        if berth in self.interesting_berths and train:
            print(f"Train {train} at berth {berth}")
            return berth, train


def run(local_map, local_berths):

    consumer = MessageConsumer(local_berths, local_map)

    sesh = Session()
    poller = WebsocketPoller(local_map)
    poller.connect(sesh, consumer)
    # TODO two threads: poller and parser
