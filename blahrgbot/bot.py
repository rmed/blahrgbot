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

from slugify import slugify

from blahrgbot.conf import SETTINGS
from blahrgbot.helper import db_field_exists, db_get_file_id, \
        db_set_file_id, db_get_all

telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(
    SETTINGS['token'],
    threaded=True,
    skip_pending=True
)

@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    """Initialize the bot."""
    response = (
        'blahrgbot\n\n'
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

@bot.message_handler(commands=['add'])
def add_scream(message):
    """Start wizard to add a new scream."""
    chat_id = message.chat.id

    if chat_id != SETTINGS['owner'] and chat_id not in SETTINGS['whitelist']:
        bot.reply_to(message, 'You do not have permissions to do that')
        return

    description = ''

    # Ask for description
    msg = bot.send_message(
        chat_id,
        'Please send me a short description of the clip to add'
    )

    bot.register_next_step_handler(
        msg,
        lambda m: process_add_desc(m, description)
    )

def process_add_desc(message, description):
    """Add a description to the clip.

    This checks whether the description already exists in the database.
    """
    chat_id = message.chat.id

    if message.content_type == 'text' and message.text == '/cancel':
        msg = bot.send_message(chat_id, 'Operation cancelled')
        return

    if message.content_type != 'text':
        msg = bot.send_message(
            chat_id,
            'Please send me a short description of the clip to add'
        )

        bot.register_next_step_handler(
            msg,
            lambda m: process_add_desc(m, description)
        )

        return

    # Check uniqueness
    if db_field_exists('desc', message.text):
        msg = bot.send_message(
            chat_id,
            'A clip with that description already exists, try again'
        )

        bot.register_next_step_handler(
            msg,
            lambda m: process_add_desc(m, description)
        )

        return

    description = message.text

    # Ask for file
    msg = bot.send_message(
        chat_id,
        'Please send me the voice clip (.ogg)\n\n'
        'I will send it back to get and ID for the clip'
    )

    bot.register_next_step_handler(
        msg,
        lambda m: process_add_clip(m, description)
    )

def process_add_clip(message, description):
    """Store the voice clip.

    This checks whether a file with that name already exists.
    """
    chat_id = message.chat.id

    if message.content_type == 'text' and message.text == '/cancel':
        msg = bot.send_message(chat_id, 'Operation cancelled')
        return

    if message.content_type != 'audio':
        msg = bot.send_message(
            chat_id,
            'Please send me the voice clip (.ogg)\n\n'
            'I will send it back to get and ID for the clip'
        )

        bot.register_next_step_handler(
            msg,
            lambda m: process_add_clip(m, description)
        )

        return

    # Download clip
    file_info = bot.get_file(message.audio.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    file_name = slugify(description) + '.ogg'

    with open(os.path.join(SETTINGS['media'], file_name), 'wb') as f:
        f.write(downloaded_file)

    # Send voice clip to get ID
    voice_msg = bot.send_voice(message.chat.id, downloaded_file)

    # Update database
    db_set_file_id(file_name, voice_msg.voice.file_id, description)

    bot.send_message(chat_id, 'New clip added')

@bot.inline_handler(lambda query: True)
def handler_inline(inline_query):
    try:
        responses = []

        for index, clip in enumerate(db_get_all()):
            r = telebot.types.InlineQueryResultCachedVoice(
                str(index),
                clip[0],
                clip[1],
                clip[1]
            )

            responses.append(r)

        bot.answer_inline_query(inline_query.id, responses)
    except Exception as e:
        print(e)
