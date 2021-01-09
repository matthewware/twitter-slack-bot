import os
import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import yaml

import asyncio
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

slack_token = os.environ['SLACK_TOKEN']
client = WebClient(token=slack_token)

############ syncronous methods ###############################################
# Syncronous writing 
def write_text(message, channel='bot-dev'):
    try:
        logging.debug('Sending message info to Slack')
        response = client.chat_postMessage(channel=channel, text=message)
        assert response["message"]["text"] == message
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"] # str like 'invalid_auth', 'channel_not_found'
        logging.error(f"Got an error: {e.response['error']}")

# syncronous write blocks to Slack
def write_block(blocks=[], user_icon="", attachments=[], channel='bot-dev'):
    try:
        logging.debug('Sending block info to Slack')
        response = client.chat_postMessage(channel=channel, 
                                           blocks=blocks,
                                           attachments=attachments,
                                           icon_url=user_icon)
        #assert response["message"]["blocks"] == blocks
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"] # str like 'invalid_auth', 'channel_not_found'
        logging.error(f"Got an error: {e.response['error']}")

############ async methods ####################################################
# These are included for completeness but are currently unused in the
# main program

async def post_message(message, channel='bot-dev'):
    try:
        response = await client.chat_postMessage(channel=channel, text=message)
        assert response["message"]["text"] == message
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

async def post_block(blocks=[], user_icon="", attachments=[], channel='bot-dev'):
    try:
        response = await client.chat_postMessage(channel=channel, 
                                                 blocks=blocks,
                                                 attachments=attachments,
                                                 icon_url=user_icon)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"] # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

# Formating Slack messages ####################################################

def build_message(t):
    """Build a Slack message as JSON 'blocks'"""
    
    if hasattr(t, 'quoted_status'):
        quote_template = [
        {
         "type":"section",
         "text":{
            "type": "mrkdwn",
            "text": "<https://twitter.com/{}|@{}> quote tweeted:".format(t.author.screen_name, t.author.screen_name)
         }
        },
        {
         "type": "section",
         "text": {
             "type": "mrkdwn",
             "text": "{}".format(t.text.split(' https://')[0])
         }
        },
        {
         "type":"context",
         "elements":[
            {
               "type":"image",
               "image_url":"{}".format(t.quoted_status.user.profile_image_url),
                "alt_text": "@{}".format(t.quoted_status.user.screen_name)
            },
            {
               "type":"mrkdwn",
               "text":"<https://twitter.com/{}|@{}> tweeted: ".format(t.quoted_status.user.screen_name, t.quoted_status.user.screen_name)
            },
            {
                "type": "mrkdwn",
                "text": "{}".format(t.quoted_status.text.split('https://')[0])
            }
         ]
        },
        ]
        if 'media' in t.entities:
            quote_template.append(
                {"type": "image",
                 "image_url": "{}".format(t.entities['media'][0]['media_url']),
                 "alt_text": "image"
                },
            )
        if 'media' in t.quoted_status.entities:
            quote_template.append(
                {"type": "image",
                 "image_url": "{}".format(t.quoted_status.entities['media'][0]['media_url']),
                 "alt_text": "image"
                },
            )
        quote_template.append(
            {
             "type":"section",
             "text":{
                "type": "mrkdwn",
                "text": "https://twitter.com/{}/status/{}".format(t.author.screen_name, t.id)
             }
            },
        )
        quote_template.append(
            {
                "type": "divider"
            }
        )
        return quote_template
    if hasattr(t, 'retweeted_status'):
        re_template = [
        {
         "type":"section",
         "text":{
            "type": "mrkdwn",
            "text": "<https://twitter.com/{}|@{}> re-tweeted:".format(t.author.screen_name, t.author.screen_name)
         }
        },
        {
         "type":"context",
         "elements":[
            {
               "type":"image",
               "image_url":"{}".format(t.retweeted_status.user.profile_image_url),
                "alt_text": "@{}".format(t.retweeted_status.user.screen_name)
            },
            {
               "type":"mrkdwn",
               "text":"<https://twitter.com/{}|@{}> tweeted: ".format(t.retweeted_status.user.screen_name, t.retweeted_status.user.screen_name)
            },
            {
                "type": "mrkdwn",
                "text": "{}".format(t.retweeted_status.text.split('https://')[0])
            }
         ]
        },
        ]
        if 'media' in t.entities:
            re_template.append(
                {"type": "image",
                 "image_url": "{}".format(t.entities['media'][0]['media_url']),
                 "alt_text": "image"
                },
            )
        if 'media' in t.retweeted_status.entities:
            re_template.append(
                {"type": "image",
                 "image_url": "{}".format(t.retweeted_status.entities['media'][0]['media_url']),
                 "alt_text": "image"
                },
            )
        re_template.append(
            {
         "type":"section",
         "text":{
            "type": "mrkdwn",
            "text": "https://twitter.com/{}/status/{}".format(t.author.screen_name, t.id)
         }
        },
        )
        re_template.append(
            {
                "type": "divider"
            }
        )
        return re_template
    else:
        template = [
        {
         "type":"section",
         "text":{
            "type": "mrkdwn",
            "text": "<https://twitter.com/{}|@{}> tweeted:".format(t.author.screen_name, t.author.screen_name)
         }
        },
        {
         "type": "section",
         "text": {
             "type": "mrkdwn",
             "text": "{}".format(t.text.split('https://')[0])
         }
        },
        ]
        if 'media' in t.entities:
            template.append(
                {"type": "image",
                 "image_url": "{}".format(t.entities['media'][0]['media_url']),
                 "alt_text": "image"
                },
            )
        template.append(
            {
             "type":"section",
             "text":{
                "type": "mrkdwn",
                "text": "https://twitter.com/{}/status/{}".format(t.author.screen_name, t.id)
             }
            },
        )
        template.append(
            {
                "type": "divider"
            }
        )
        return template

if __name__ == "__main__":

    # test basic functionality
	client = AsyncWebClient(token=slack_token)
	asyncio.run(post_message("Posted asynchronously", channel='bot-dev'))
