# -*- coding=utf-8 -*-
"""
"""

import logging
import os
import re
import requests
import xmltodict

from wechaty import (
    Contact,
    FileBox,
    Message,
    MessageType,
    Wechaty,
)

logging.basicConfig(level=logging.ERROR)
log = logging.getLogger(__name__)

class MessageHandler():
    def __init__(self, bot):
        self._bot = bot
        self._counter = 0
        self._cmds_re = re.compile(r'#(\w+) (.*)')
        self._keywords = [
            ['额度'],
            ['融资', '10倍'],
            ['融资', '20倍'],
        ]

    def message_contains_words(self, text: str, keywords: list):
        for keyword in keywords:
            if keyword not in text:
                return False
        return True

    async def handle(self, msg: Message):
        self._counter += 1
        log.error('received %s messages' % self._counter)
        me = self._bot.Contact.load('paulhybryant0104')
        text = msg.text()
        mention_self = await msg.mention_self()
        mention_text = await msg.mention_text()
        if msg.room():
            topic = await msg.room().topic()
            log.error('room: %s, topic %s' % (msg.room().room_id, topic))
            forward = self.handle_room(topic, text, mention_self, mention_text, msg.room().room_id, msg.type())
            if forward:
                await me.say('来自群: %s' % topic)
                if msg.type() == MessageType.MESSAGE_TYPE_ATTACHMENT:
                    filebox = await msg.to_file_box()
                    await me.say(filebox)
                else:
                    await msg.forward(me)
        else:
            log.error(msg)
            result = self.handle_cmd(text)
            if result:
                log.error(result)
                await me.say(result)

    def handle_room(self, topic, text, mention_self, mention_text, room_id, msg_type):
        # @me
        if mention_self:
            log.error('mentioned me')
            return True
        # @all
        elif '@所有人' in mention_text or '@All' in mention_text:
            log.error('mentioned all')
            return True
        # For testing
        elif room_id == '26833418609@chatroom':
            if  msg_type == MessageType.MESSAGE_TYPE_ATTACHMENT:
                return True
        # TODO: Automatically cache chatroom ids, given topic (room name)
        # TODO: Only forward file from specific talker
        # 低风险投资3群
        elif room_id == '4932234304@chatroom':
            if msg_type == MessageType.MESSAGE_TYPE_ATTACHMENT:
                return True
        # 投资学习8群
        elif room_id == '17346331234@chatroom':
            if msg_type == MessageType.MESSAGE_TYPE_ATTACHMENT:
                return True
        else:
            for keywords in self._keywords:
                if self.message_contains_words(text, keywords):
                    log.error('contains keywords: %s' % keywords)
                    return True
        return False

    def handle_cmd(self, cmd):
        if cmd.startswith('#'):
            m = self._cmds_re.match(cmd)
            if m:
                try:
                    cmd = getattr(self, m.group(1))
                    return cmd(m.group(2))
                except AttributeError:
                    return ('Unimplemented command: %s' % m.group(1))
            else:
                return ('Invalid command: %s' % cmd)
        return None

    # args: 'city'
    def weather(self, args: str):
        r = requests.get('http://wthrcdn.etouch.cn/weather_mini?city=%s' % args)
        r.encoding = 'utf-8'
        if r.status_code == 200:
            data = r.json()['data']['forecast'][0]
            return '%s%s天气： %s - %s， %s%s， %s' % (args, data['date'], data['low'], data['high'], data['fengxiang'], data['fengli'], data['type'])
        else:
            return 'Failure status: %s' % r.status_code
