# -*- coding: utf-8 -*-
#
# blahrgbot
# https://github.com/rmed/blahrgbot
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Rafael Medina García <rafamedgar@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Telegram bot implementation."""

import logging
import os
import telebot

from blahrgbot.conf import SETTINGS, db_get_file_id, db_set_file_id, db_get_aah

telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(
    SETTINGS['token'],
    threaded=True,
    skip_pending=True
)

@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    """Initialize the bot."""
    response = ('blahrgbot\n\n'
                'Call me from any chat when in need!'
               )

    bot.reply_to(message, response)

@bot.message_handler(commands=['refresh'])
def handle_refresh(message):
    """Refresh media directory and upload new clips if not present."""
    # Check permissions
    if message.chat.id != SETTINGS['owner']:
        bot.reply_to(message, 'You are not the owner of this bot')
        return

    for clip in os.listdir(SETTINGS['media']):
        file_id = db_get_file_id(clip)

        if not file_id:
            # Must send file
            with open(os.path.join(SETTINGS['media'], clip), 'rb') as f:
                msg = bot.send_voice(message.chat.id, f)

                db_set_file_id(clip, msg.voice.file_id)

    bot.reply_to(message, 'Clips refreshed!')

@bot.message_handler(commands=['me'])
def me(message):
    """Get user ID."""
    bot.reply_to(message, message.chat.id)

@bot.inline_handler(lambda query: True)
def handler_inline(inline_query):
    try:
        r = telebot.types.InlineQueryResultCachedVoice(
            '1',
            db_get_aah(),
            'AAAAAAAAAAAH',
        )
        bot.answer_inline_query(inline_query.id, [r])
    except Exception as e:
        print(e)
