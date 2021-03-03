# -*- coding=utf-8 -*-
import unittest

from handler import MessageHandler

class BotTest(unittest.TestCase):

    def test_weather(self):
        handler = MessageHandler(None)
        #  result = handler.weather('北京 北京 海淀')
        #  self.assertRegex(result, '海淀 .*')
        result = handler.weather('北京')
        self.assertRegex(result, '北京.*天气： .*')

    def test_message_contains_keywords(self):
        handler = MessageHandler(None)
        result = handler.message_contains_words('9:30放额度，最高20倍，手慢无', ['额度', '20倍'])
        self.assertEqual(result, True)

    def test_handle_cmd(self):
        handler = MessageHandler(None)
        result = handler.handle_cmd('#weather 北京')
        self.assertRegex(result, '北京.*天气： .*')
        result = handler.handle_cmd('#run test')
        self.assertRegex(result, 'Unimplemented command: .*')
        result = handler.handle_cmd('#@$ test')
        self.assertRegex(result, 'Invalid command: .*')

if __name__ == '__main__':
    unittest.main()
