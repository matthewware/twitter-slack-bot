import yaml
import http
import hmac
import hashlib
import sys
import time
import os

from flask import Flask, request

import db as db

try:
    config = yaml.safe_load(open('config.yaml'))
except yaml.YAMLError as exc:
    print(exc)

SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
debug = False

def verify_slack_request(timestamp, signature):
    # mostly copied from the slackeventapi ->
    # https://github.com/slackapi/python-slack-events-api
    #
    # See also the Slack documentation:
    # https://api.slack.com/authentication/verifying-requests-from-slack
    #
    # and the function:
    # from slack_sdk.signature import SignatureVerifier

    # Verify the request signature of the request sent from Slack
    # Generate a new hash using the app's signing secret and request data

    # Compare the generated hash and incoming request signature
    # Python 2.7.6 doesn't support compare_digest
    # It's recommended to use Python 2.7.7+
    # noqa See https://docs.python.org/2/whatsnew/2.7.html#pep-466-network-security-enhancements-for-python-2-7

    if abs(time.time() - int(timestamp)) > 60 * 5:
        # The request timestamp is more than five minutes from local time.
        # It could be a replay attack, so let's ignore it.
        return False

    req = str.encode('v0:' + str(timestamp) + ':') + request.get_data()
    request_hash = 'v0=' + hmac.new(
        str.encode(SLACK_SIGNING_SECRET),
        req, hashlib.sha256
    ).hexdigest()

    if hasattr(hmac, "compare_digest"):
        # Compare byte strings for Python 2
        if (sys.version_info[0] == 2):
            return hmac.compare_digest(bytes(request_hash), bytes(signature))
        else:
            return hmac.compare_digest(request_hash, signature)
    else:
        if len(request_hash) != len(signature):
            return False
        result = 0
        if isinstance(request_hash, bytes) and isinstance(signature, bytes):
            for x, y in zip(request_hash, signature):
                result |= x ^ y
        else:
            for x, y in zip(request_hash, signature):
                result |= ord(x) ^ ord(y)
        return result == 0

def create_app():
    app = Flask(__name__)

    @app.route('/slack/events', methods=['POST'])
    def process_slash():
        # verify slack request
        req_timestamp = request.headers.get('X-Slack-Request-Timestamp')
        slack_signature = request.headers.get('X-Slack-Signature')
        is_good = verify_slack_request(req_timestamp, slack_signature)

        if debug:
            if is_good: print("Verified Slack request!")
            print("command: " + request.form['command'])
            print("text: " + request.form['text'])
            print("response_url" + request.form['response_url'])
            print("timestamp: " + request.headers.get('X-Slack-Request-Timestamp'))

        if is_good:
            # always return empty OK so Slack knows we got the message
            if request.form['command'] == '/users':
                return (str(db.get_users()), http.HTTPStatus.OK)
            if request.form['command'] == '/keywords':
                return (str(db.get_keywords()), http.HTTPStatus.OK)
            if request.form['command'] == '/add_user':
                db.add_user(request.form['text'])
                return (request.form['text'] + " added to users", http.HTTPStatus.OK)
            if request.form['command'] == '/add_keyword':
                db.add_keyword(request.form['text'])
                return (request.form['text'] + " added to keywords", http.HTTPStatus.OK)
            if request.form['command'] == '/remove_user':
                db.remove_user(request.form['text'])
                return (request.form['text'] + " removed from users", http.HTTPStatus.OK)
            if request.form['command'] == '/remove_keyword':
                db.remove_keyword(request.form['text'])
                return (request.form['text'] + " removed from keywords", http.HTTPStatus.OK)
            if request.form['command'] == '/help':
                return (help_message, http.HTTPStatus.OK)
        else:
            return ("", http.HTTPStatus.FORBIDDEN)

    return app

help_message = {
    "attachments": [
        {
            "color": "#39a2f7",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "These are the avaliable TwitterBot commands:\n>`/users` view accounts I'm following \n>`/keywords` view keywords I'm searching for\n>`/add_user` add a Twitter account\n>`/add_keyword` add a keyword to search for\n>`/remove_user` remove a Twitter account\n>`/remove_keyword` remove a keyword search term\n>`/help` print help"
                    }
                }
            ]
        }
    ]
}

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0',port=config['control_port'])
