#!/bin/sh

# This is notional and you should edit to match your environment and
# python/PATH/envs etc...
#conda activate slackbot

# start control server
nohup python server.py --log=WARNING &
# start twitter stream
nohup python twitter.py --log=WARNING &
