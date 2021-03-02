# -*- coding=utf-8 -*-
import unittest

from handler import MessageHandler

class BotTest(unittest.TestCase):

    def test_weather(self):
        handler = MessageHandler(None)
        #  result = handler.weather('北京 北京 海淀')
        #  self.assertRegex(result, '海淀 .*')
        result = handler.weather('北京')
        print(result)
        self.assertRegex(result, '北京.*天气： .*')

    def test_message_contains_keywords(self):
        handler = MessageHandler(None)
        result = handler.message_contains_words('9:30放额度，最高20倍，手慢无', ['额度', '20倍'])
        self.assertEqual(result, True)

if __name__ == '__main__':
    unittest.main()
