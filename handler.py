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
        #  self._weather_data = {}
        #  with open('weather.xml', 'r') as f:
            #  xml = xmltodict.parse(f.read())
            #  for province in xml['China']['province']:
                #  self._weather_data[province['@name']] = {}
                #  cities = None
                #  if isinstance(province['city'], list):
                    #  cities = province['city']
                #  else:
                    #  cities = [province['city']]
                #  for city in cities:
                    #  self._weather_data[province['@name']][city['@name']] = {}
                    #  counties = None
                    #  if isinstance(city['county'], list):
                        #  counties = city['county']
                    #  else:
                        #  counties = [city['county']]
                    #  for county in counties:
                        #  self._weather_data[province['@name']][city['@name']][county['@name']] = county['@weatherCode']

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
            forward = handle_room(topic, text, mention_self, mention_text, msg.room().room_id, msg.type())
            if forward:
                await msg.say('来自群: %s' % topic)
                await msg.forward(me)
        else:
            log.error(msg)
            result = handle_cmd(text)
            if result:
                log.error(result)
                await msg.say(result)

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

    # args: 'province city county'
    def weather_deprecated(self, args: str):
        params = args.split(' ')
        if len(params) != 3:
            return 'Invalid argument to command: %s, expecting <province city county>'
        else:
            r = requests.get('http://www.weather.com.cn/data/sk/%s.html' % self._weather_data[params[0]][params[1]][params[2]])
            r.encoding = 'utf-8'
            if r.status_code == 200:
                return '%s %s %s' % (r.json()['weatherinfo']['city'], r.json()['weatherinfo']['WD'], r.json()['weatherinfo']['temp'])
            else:
                return 'Failure status: %s' % r.status_code
