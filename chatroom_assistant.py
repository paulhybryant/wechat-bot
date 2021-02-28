# -*- coding=utf-8 -*-
"""
"""
import os
import asyncio
import logging

from wechaty import (
    Contact,
    FileBox,
    Message,
    MessageType,
    Wechaty,
)

logging.basicConfig(level=logging.ERROR)
log = logging.getLogger(__name__)
bot = None
counter = 0

KEYWORDS=['额度']

async def on_message(msg: Message):
    """
    Message Handler for the Bot
    """
    global counter
    counter += 1
    log.error('received %s messages' % counter)
    me = bot.Contact.load('paulhybryant0104')
    text = msg.text()
    mention_self = await msg.mention_self()
    mention_text = await msg.mention_text()
    if msg.room():
        topic = await msg.room().topic()
        log.error('room: %s, topic %s' % (msg.room().room_id, topic))
        # @me
        if mention_self:
            log.error('mentioned me')
            await me.say('来自群: %s' % topic)
            await msg.forward(me)
        # @all
        elif '@所有人' in mention_text or '@All' in mention_text:
            log.error('mentioned all')
            await me.say('来自群: %s' % topic)
            await msg.forward(me)
        # For testing
        elif topic == 'MyAssistant':
            log.error(msg)
            if msg.type() == MessageType.MESSAGE_TYPE_ATTACHMENT:
                filebox = await msg.to_file_box()
                await me.say(filebox)
        # 低风险投资3群
        elif msg.room().room_id == '4932234304@chatroom':
            if msg.type() == MessageType.MESSAGE_TYPE_ATTACHMENT:
                filebox = await msg.to_file_box()
                await me.say(filebox)
        # TODO: Automatically cache chatroom ids, given topic (room name)
        elif topic == '投资学习8群':
            log.error(msg.room().room_id)
            if msg.type() == MessageType.MESSAGE_TYPE_ATTACHMENT:
                filebox = await msg.to_file_box()
                await me.say(filebox)
        else:
            for keyword in KEYWORDS:
                if keyword in text:
                    log.error('contains keyword: %s' % keyword)
                    await me.say('来自群: %s' % topic)
                    await msg.forward(me)
    else:
        log.error(msg)
        if text == '#weather':
            await msg.say('TODO: report today\'s weather')


async def on_scan(qrcode: str, status: int, data):
    """
    Scan Handler for the Bot
    """
    print('Status: ' + status + ', View QR Code Online: https://wechaty.github.io/qrcode/' + str(qrcode))


async def on_login(user: Contact):
    """
    Login Handler for the Bot
    """
    print(user)

async def main():
    """
    Async Main Entry
    """
    #
    # Make sure we have set WECHATY_PUPPET_SERVICE_TOKEN in the environment variables.
    #
    if 'WECHATY_PUPPET_SERVICE_TOKEN' not in os.environ:
        print('''
            Error: WECHATY_PUPPET_SERVICE_TOKEN is not found in the environment variables
            You need a TOKEN to run the Java Wechaty. Please goto our README for details
            https://github.com/wechaty/python-wechaty-getting-started/#wechaty_puppet_service_token
        ''')

    global bot
    bot = Wechaty()

    bot.on('scan',      on_scan)
    bot.on('login',     on_login)
    bot.on('message',   on_message)

    await bot.start()

    print('[Python Wechaty] My Assistant Bot started.')


asyncio.run(main())
