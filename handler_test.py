# -*- coding=utf-8 -*-
import unittest

from handler import MessageHandler
from wechaty import (
    FileBox,
    MessageType,
)

class BotTest(unittest.TestCase):

    def test_weather(self):
        handler = MessageHandler(None)
        result = handler.weather('北京')
        self.assertRegex(result, '北京.*天气： .*')

    def test_message_contains_keywords(self):
        handler = MessageHandler(None)
        result = handler.message_contains_words('9:30放额度，最高20倍，手慢无', ['额度', '20倍'])
        self.assertEqual(result, True)

    def test_doc2pdf(self):
        handler = MessageHandler(None)
        filebox = FileBox.from_file("testdata/Test.docx")
        result, error = handler.doc2pdf(filebox, "Test")
        self.assertEqual(result, "/tmp/Test.pdf")

    def test_handle_cmd(self):
        handler = MessageHandler(None)
        result = handler.handle_cmd('#weather 北京')
        self.assertRegex(result, '北京.*天气： .*')
        result = handler.handle_cmd('#run test')
        self.assertRegex(result, 'Unimplemented command: .*')
        result = handler.handle_cmd('#@$ test')
        self.assertRegex(result, 'Invalid command: .*')

    def test_handle_room(self):
        handler = MessageHandler(None)
        # mentioned me
        forward = handler.handle_room('测试群', '测试', True, '', 'id', None)
        self.assertTrue(forward)

        # mentioned all
        forward = handler.handle_room('测试群', '测试', False, '@All', 'id', None)
        self.assertTrue(forward)

        # specific room, has attachment
        forward = handler.handle_room('测试群', '测试', False, '', '4932234304@chatroom', MessageType.MESSAGE_TYPE_ATTACHMENT)
        self.assertTrue(forward)

        # specific room, no attachment
        forward = handler.handle_room('测试群', '测试', False, '', '4932234304@chatroom', None)
        self.assertFalse(forward)

        # keywords match
        forward = handler.handle_room('测试群', '有额度', False, '', '', None)
        self.assertTrue(forward)

        # no keywords match
        forward = handler.handle_room('测试群', '测试', False, '', '4932234304@chatroom', None)
        self.assertFalse(forward)

        # skipped
        forward = handler.handle_room('测试群', '测试', False, '', 'id', None)
        self.assertFalse(forward)

if __name__ == '__main__':
    unittest.main()
