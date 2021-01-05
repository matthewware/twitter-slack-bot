#!/bin/sh

# This is notional and you should edit to match your environment and
# python/PATH/envs etc...
#conda activate slackbot

# start control server
nohup python server.py >> /var/log/twitter/twitter-control-server.log 2>&1 &
# start twitter stream
nohup python twitter.py >> /var/log/twitter/twitter-bot.log 2>&1 &
