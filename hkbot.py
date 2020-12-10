#!/usr/bin/env python3

###################################
# p2p bitcoin hk bot for keybase
###################################

import asyncio
import logging
import os
import sys
from pyjokes import pyjokes
import random
import pykeybasebot.types.chat1 as chat1
from pykeybasebot import Bot
from dbtools import add_doc, find_active_offers, find_all_offers, delete_alldocs_by_user, delete_entry, parse_offers
import datetime as dt

logging.basicConfig(level=logging.DEBUG)

if "win32" in sys.platform:
    # Windows specific event-loop policy
    asyncio.set_event_loop_policy(
        asyncio.WindowsProactorEventLoopPolicy()  # type: ignore
    )


async def handler(bot, event):
    async def advertize_commands(
            bot, channel: chat1.ChatChannel, message_id: int
    ) -> chat1.SendRes:
        await bot.ensure_initialized()
        payload = {
            "method": "advertisecommands",
            "params": {
                "options": {
                    "advertisements": [
                        {"type": "public",
                         "commands": [
                             {"name": "help",
                              "description": "Get help using this bot"},
                             {"name": "add",
                              "description": "Add an Offer to Buy or Sell, Example: \n\nBuy 0.05 btc, %Coinbase\n HKD FPS/ATM/Cash"},
                             {"name": "all",
                              "description": "List Existing Offers"},
                             {"name": "del",
                              "description": "Delete an Offer: !Del [username] [offer_number]"},
                             {"name": "joke",
                              "description": "Forces me to tell a programing oriented joke."},
                         ]}]}}}
        if os.environ.get('KEYBASE_BOTALIAS') != "":
            payload['params']['options']['alias'] = os.environ.get('KEYBASE_BOTALIAS')

        res = await bot.chat.execute(payload)

    if event.msg.content.type_name != chat1.MessageTypeStrings.TEXT.value:
        return
    if event.msg.content.type_name != chat1.MessageTypeStrings.TEXT.value:
        return
    if event.msg.content.text.body == '!update':
        conversation_id = event.msg.conv_id
        msg_id = event.msg.id
        await advertize_commands(bot, event.msg.conv_id, event.msg.id)
        await bot.chat.react(conversation_id, msg_id, ":white_check_mark:")

    if str(event.msg.content.text.body).startswith("!help"):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        help_msg = """```
            Here are the commands I currently am enslaved to:
            !all - List Open Offers.
            !add - Add an Offer, Ex: Buy 0.05 btc, %Coinbase HKD FPS/ATM/Cash.
            !del - Delete an offer. !Del [username] [offer_number]
            !joke - Forces me to tell a joke. For the love of God just don't.
            !help - Prints this list.
            !update - Update's the list of available autocomplete botcommands.
            ```"""
        await bot.chat.send(conversation_id, help_msg)

    if str(event.msg.content.text.body).startswith("!joke"):
        observations = ["It didn't work for me. . .", "I am so sorry.",
                        "I'll be in my room trying to purge my memory banks.",
                        "Why must you keep making me do this?",
                        "This is your fault.",
                        "I've made it worse. . ."]
        joke = ""
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        joke += "I hope this cheers you up.```"
        joke += pyjokes.get_joke()
        joke += f"```{random.choice(observations)}"
        await bot.chat.send(conversation_id, joke)

    if str(event.msg.content.text.body).startswith("!add"):
        channel = event.msg.channel
        msg_id = event.msg.id
        body = event.msg.content.text.body
        offer = body.split("!add")[1]
        conversation_id = event.msg.conv_id
        print(f'conver. id {conversation_id}')
        print(f'msg_id : {msg_id}')
        username = event.msg.sender.username
        print(f'username: {username}')
        print(event.msg)
        if len(offer) > 0:
            post = {
                'username': username,
                'offer': offer,
                'active' : True,
                'initdate': dt.datetime.now()
            }
            result = add_doc(post)
            if result != -1:
                msg = f"Ok I've added your offer message, @{username}"
                await bot.chat.send(conversation_id, msg)
            elif result == -1:
                msg = f"Error  - Couldn't add, please contact an admin."
                await bot.chat.send(conversation_id, msg)
        else:
            msg = f"Error - No Content - Please give an offer"
            await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith("!all"):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        msg = "Here's a current list of Open Offers:\n"
        result = find_all_offers()
        offers = parse_offers(result)
        msg = msg + offers
        if len(offers) > 0:
            await bot.chat.send(conversation_id, msg)
        else:
            msg = "Currently, there are No Offers\n"
            await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith("!del"):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        username = event.msg.sender.username
        body = event.msg.content.text.body
        print(f'arguments: {body}')
        id = body.split("!del")[1].strip()
        count = delete_entry(username, id)
        if count == 1:
            msg = f"Ok I've deleted your offer, @{username}"
            await bot.chat.send(conversation_id, msg)
        else:
            msg = f"Sorry I can't find this order ID, @{username}"
            await bot.chat.send(conversation_id, msg)

    if str(event.msg.content.text.body).startswith("!duser"):
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        body = event.msg.content.text.body
        user = body.split("!duser")[1].strip()
        count = delete_alldocs_by_user(user)
        if count:
            msg = f"{count} offers by @{username} deleted\n"
            await bot.chat.send(conversation_id, msg)
        else:
            msg = f"couldn't find offers by @{username}\n"
            await bot.chat.send(conversation_id, msg)
    
    if f"{os.environ.get('KEYBASE_BOTNAME')}" in str(event.msg.content.text.body).lower():
        channel = event.msg.channel
        msg_id = event.msg.id
        conversation_id = event.msg.conv_id
        await bot.chat.react(conversation_id, msg_id, ":tada:")


listen_options = {
    "local": False,
    "wallet": False,
    # "dev": True,
    "hide-exploding": False,
    "convs": True,
    "filter_channel": {"name": f"{os.environ.get('TEAM_NAME')}", "topic_name": "test1", "members_type": "team"},
    # "filter_channel": None,
    # "filter_channels": None,
}

bot = Bot(username=f"{os.environ.get('KEYBASE_BOTNAME')}",
          paperkey=os.environ.get('KEYBASE_PAPERKEY'),
          handler=handler,
          home_path=f'./{os.environ.get("KEYBASE_BOTNAME")}')

asyncio.run(bot.start(listen_options=listen_options))
