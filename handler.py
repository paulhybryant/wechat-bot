# -*- coding=utf-8 -*-
"""
"""

import logging
import os
import re
import requests
import subprocess

from google_trans_new import google_translator
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
        self._cmds_re = re.compile(r'#(\w+) ?(.*)')
        self._keywords = [
            ['额度'],
            ['融资', '10倍'],
            ['融资', '20倍'],
        ]
        self._subscriptions = [
            '复利先生',
            '持有封基',
            '复利人生',
            '投机箴言',
            '唐书房',
            '股市药丸',
            '财富严选',
            '盛唐风物',
            '爱投资的小熊猫',
            '郭二侠鑫金融',
            '萌哥阵地',
            '量化简财',
            '涛哥讲新股',
            '老郭聊新股',
            '站在Ju人肩上A',
            '新股渔夫',
        ]
        self._config = {}

    def message_contains_words(self, text: str, keywords: list):
        for keyword in keywords:
            if keyword not in text:
                return False
        return True

    # TODO: Use asyncio unittest to test the code here
    # TODO: Use wechaty-mock for testing
    async def handle(self, msg: Message):
        self._counter += 1
        log.error('received %s messages' % self._counter)
        me = self._bot.Contact.load('paulhybryant')
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
            log.error('Message: %s, Contact: %s, Name: %s' % (msg, msg.talker(), msg.talker().name))
            result = self.handle_cmd(text)
            if result:
                log.error(result)
                await msg.say(result)

            if msg.talker().contact_id in ['wxid_p7xyfpcx7aoa12', 'wxid_5av5yw0udmgp12'] and msg.type() == MessageType.MESSAGE_TYPE_ATTACHMENT:
                filebox = await msg.to_file_box()
                doc_re = re.compile(r'(.*)\.docx?')
                m = doc_re.match(filebox.name)
                if m:
                    if self._config.get('doc2pdf', True):
                        f = '/tmp/%s' % filebox.name
                        await filebox.to_file(f, True)
                        converted, error = self.doc2pdf(f, m.group(1))
                        if converted:
                            pdf = filebox.from_file(converted)
                            await me.say(pdf)

            if msg.type() == MessageType.MESSAGE_TYPE_URL:
                talker = msg.talker()
                if talker.name in self._subscriptions:
                    await me.say('来自公众号： %s' % talker.name)
                    await msg.forward(me)

    def doc2pdf(self, f, basename):
        # soffice is not available in my environment, yikes!
        # result = subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', f], capture_output=True)
        result = subprocess.run(['./doc2pdf.sh', f], capture_output=True)
        if result.returncode == 0:
            return ('/tmp/%s.pdf' % basename, None)
        else:
            return (None, result.stdout)

    def handle_room(self, topic: str, text: str, mention_self: bool, mention_text: str, room_id: str, msg_type: MessageType):
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
        # 低风险投资乙群
        elif room_id == '18578335159@chatroom':
            if msg_type == MessageType.MESSAGE_TYPE_ATTACHMENT:
                return True
        # 投资学习9群
        elif room_id == '20282708242@chatroom':
            if msg_type == MessageType.MESSAGE_TYPE_ATTACHMENT:
                return True
        else:
            for keywords in self._keywords:
                if self.message_contains_words(text, keywords):
                    log.error('contains keywords: %s' % keywords)
                    return True
        return False

    def handle_cmd(self, cmd: str):
        if cmd.startswith('#'):
            m = self._cmds_re.match(cmd)
            if m:
                cmd = m.group(1)
                try:
                    fn = getattr(self, cmd)
                    return fn(m.group(2))
                except AttributeError:
                    return (f'Unimplemented command: {cmd}')
            else:
                return (f'Invalid command: {cmd}')
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

    # args: 'text to translate'
    def translate(self, args: str):
        translator = google_translator()
        return translator.translate(args)

    def enable(self, args: str):
        if args in ['enable', 'disable']:
            return 'Cannot enable / disable command %s' % args
        self._config[args] = True

    def disable(self, args: str):
        if args in ['enable', 'disable']:
            return 'Cannot enable / disable command %s' % args
        self._config[args] = False

    # args: 'file name'
    def files(self, args: str):
        if args:
            if os.path.exists('files/%s' % args):
                return FileBox.from_file('files/%s' % args)
            return 'file %s not exists' % args
        else:
            return str(os.listdir('files'))
