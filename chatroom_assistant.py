# -*- coding=utf-8 -*-
"""
"""
import asyncio
from handler import MessageHandler

from wechaty import (
    Contact,
    Wechaty,
)

bot = None
handler = MessageHandler()

async def on_message(msg: Message):
    """
    Message Handler for the Bot
    """
    global handler
    handler.handle(msg)


async def on_scan(qrcode: str, status: int, data):
    """
    Scan Handler for the Bot
    """
    print('Status: ' + status + ', View QR Code Online: https://wechaty.github.io/qrcode/' + str(qrcode))


async def on_login(user: Contact):
    """
    Login Handler for the Bot
    """
    print('%s logged in' % user)

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

    print('[Python Wechaty] Chatroom Assistant started.')


asyncio.run(main())
