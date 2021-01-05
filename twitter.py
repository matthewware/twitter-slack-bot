import sys
import os
import time

from tweepy import Stream
import tweepy
import db as db
import slack as slack
import yaml
from watchgod import run_process, watch
from watchgod.watcher import DefaultDirWatcher

try:
    config = yaml.safe_load(open('config.yaml'))
except yaml.YAMLError as exc:
    print(exc)

TWITTER_CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
TWITTER_CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

POST_CHANNEL = config['channel']

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# Create custom Classes #######################################################

class CSVWatcher(DefaultDirWatcher):
    def should_watch_file(self, entry):
        return entry.name.endswith(('.csv',))

class CustTweepyStream(Stream):
    """Custom Stream usable in contexts"""
    def finalize(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finalize()

    def __enter__(self):
        return self

# Brute force filtering functions #############################################
def filter_tweets_by_word(status):
    """Brute-force search"""
    flag = False

    # search tweet text
    for word in db.get_keywords():
        for w in status.text.split():
            if word == w:
                flag = True
    # search quote tweet text
    if hasattr(status, "quoted_status"):
        for word in db.get_keywords():
            for w in status.quoted_status.text.split():
                if word == w:
                    flag = True
    # search retweet text
    if hasattr(status, "retweeted_status"):
        for word in db.get_keywords():
            for w in status.retweeted_status.text.split():
                if word == w:
                    flag = True
    return flag

def filter_tweets_by_user(twitter_user):
    """Brute-force search"""
    flag = False
    for user in db.get_users():
        if user == '@' + str(twitter_user):
            flag = True
    return flag
###############################################################################

def preprocess_text(status):
    """
    convert extended tweets text and full text tweets
    to something our template can handle
    """
    if hasattr(status, "full_text"):
        status.text = status.full_text
    if hasattr(status, "extended_tweet"):
        status.text = status.extended_tweet["full_text"]
    if hasattr(status, "quoted_status"):
        if hasattr(status.quoted_status, "full_text"):
            status.quoted_status.text = status.quoted_status.full_text
    if hasattr(status, "retweeted_status"):
        if hasattr(status.retweeted_status, "full_text"):
            status.retweeted_status.text = status.retweeted_status.full_text
    return status

#override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):

    def __init__(self, channel='bot-dev', debug=False):
        super(MyStreamListener,self).__init__()
        self.debug = debug
        self.channel = channel
        
    def on_status(self, status):
        if self.debug: print("Got a tweet!")
        
        status = preprocess_text(status)
            
        # parse for authors
        if filter_tweets_by_user(status.user.screen_name):
            if self.debug: print("found an author match")
            # parse for keywords
            if filter_tweets_by_word(status):
                if self.debug: print("found a text match!")
                # filter out reply tweets
                if status.in_reply_to_status_id == None:
                    slack.write_block(slack.build_message(status), 
                                user_icon=status.user.profile_image_url, 
                                channel=self.channel)

    def on_error(self, status_code):
        print("Recieved error code: {}".format(status_code))
        if status_code == 420:
            # request rate limit
            print("API rate limited!! Waiting 60s and will try to restart")
            time.sleep(60)
            bot_stream = launch_bot()

            for changes in watch(os.path.abspath('.'), watcher_cls=CSVWatcher):
                print(changes)
                bot_stream = restart_bot(bot_stream)

        return False

def get_ids():
    """Helper to get Twitter id numbers from user handles"""
    users = db.get_users()
    ids = []
    for user in users:
        ids.append(str(api.get_user(screen_name = user).id))
    return ids

def launch_bot(channel=POST_CHANNEL, debug=True):
    """
    Start the stream and filter for users in the db list.
    All other filtering is done by the Listener.
    """
    print("Creating listener...")
    myStreamListener = MyStreamListener(channel=channel, debug=debug)
    myStream = CustTweepyStream(auth = api.auth, 
                                listener=myStreamListener, 
                                include_entities=True, 
                                tweet_mode = 'extended')

    # start filtering
    print("Starting bot...")
    # async needs to be true so we don't block the file watcher
    myStream.filter(follow=get_ids(), is_async=True)

    return myStream

def restart_bot(stream, debug=False):
    # try to kill previous stream
    stream.disconnect()
    # return a new stream but wait some time to avoid rate limiting
    time.sleep(60)
    return launch_bot(debug=debug)

if __name__ == '__main__':
    dev_mode = False
    # run the bot watching for file changes using CSVWatcher
    bot_stream = launch_bot(debug=dev_mode)

    for changes in watch(os.path.abspath('.'), watcher_cls=CSVWatcher):
        if dev_mode:
            print(changes)
            bot_stream = restart_bot(bot_stream, debug=dev_mode)
        else:
            bot_stream = restart_bot(bot_stream)
