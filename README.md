# Twitter-Slack bot

Bot for streaming tweets to a slack channel written in python with 
[Tweepy](https://github.com/tweepy/tweepy) and 
[slack_sdk](https://github.com/slackapi/python-slack-sdk).

  * Uses Twitter Stream API
  * Filters for users and keywords
  * Allows dynamic update of users and keywords

A notional example of how to start the bot is given in the `start_servers.sh` 
script. Example `keywords.csv` and `user.csv` files are provided. Edit them 
to match the users and words you'd like to follow. Also, update the 
`config.yaml` file to match your preference for Slack channel etc... You
should be able to create a 'slackbot' conda environment with the 
`environment.yaml` file:

```bash
conda env create -f environment.yaml
```

For more detail see the [blog post](https://matthewware.dev/Twitter-Bots/). Also keep
in mind that Slack has made changes to its authentication and can do that without much
warning. If you start getting `is_archived` or other errors from a working setup, the 
first thing to try is regenerating the `SLACK_TOKEN` and possibly the
`SLAKC_SIGNING_SECRET`.

## Authentication

You'll need to authenticate with Slack and Twitter. Go to the [Twitter 
developer portal](https://developer.twitter.com/en) and request developer 
tokens and secrets if you don't already have them. For Slack, 
[your bot](https://slack.com/help/articles/115005265703-Create-a-bot-for-your-workspace) 
will have its own token and signing secret. Export them to your server-side 
environment:

```bash
$ export SLACK_TOKEN='XXXX-XXXXXXXXXXXX-XXXXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXX'
$ export SLACK_SIGNING_SECRET='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
$ export TWITTER_CONSUMER_KEY='XXXXXXXXXXXXXXXXXXXXXXXX'
$ export TWITTER_CONSUMER_SECRET='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
$ export TWITTER_ACCESS_TOKEN='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
$ export TWITTER_ACCESS_TOKEN_SECRET='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
```

The Twitter Stream and control server will expect to find them in the environment.

## Slash commands

To allow users in the Slack channel to update the users and keywords, you'll 
need to set up the slash commands in Slack and open the server port for 
`server.py` to use. Check the [slack api doc](https://api.slack.com/interactivity/slash-commands)
for more information. The names need to match exactly `/help`, `/users`, 
`/keywords`, `/add_user`, `/add_keyword`, `/remove_user`, `/remove_keyword`.

## Deployment

Please don't run these processes as root. Use common sense for 
scalability and security. For my use case, the volume of tweets and commands
made most of the scalability best practices unnecessary.

## Possible new features:
  - [ ] Use async methods with Slack
  - [ ] Write to multiple channels
  - [ ] Separate context for multiple conversations
  - [x] Proper logging
