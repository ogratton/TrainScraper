from trains import MessageConsumer

import unittest


class TestMessageConsumer(unittest.TestCase):

    def setUp(self) -> None:
        local_berths = [
            "WY0118",
            "WS0004",
            "WS0002",
        ]
        local_map = "lec1"

        self.consumer = MessageConsumer(local_berths, local_map)

        self.messages = [
            ["OTT.MAP.lec1", {"e": "WY0118", "a": {"t": "BTH", "descr": "1A16"}}],
            ["OTT.MAP.lec1", {"e": "WS0004", "a": {"t": "BTH"}}],
            ["OTT.MAP.lec1", {"e": "WS0002", "a": {"t": "BTH", "descr": "2C18", "uid": "L42056", "date": "2020-02-23"}}],
        ]

    def test_check_messages(self):
        res = self.consumer.parse_message_list(self.messages)
        self.assertListEqual([('WS0002', 'L42056')], list(res))
