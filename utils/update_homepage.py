import os
from slack_sdk import WebClient

new_token = os.environ['SLACK_TOKEN']
client = WebClient(token=new_token)

user_id = "YOUR USER ID HERE"

data = {
  "type": "home",
  "title": {
    "type": "plain_text",
    "text": "Title"
      },
  "type": "home",
  "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "A simple Twitter bot"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "These are the avaliable TwitterBot commands:\n>`/users` view accounts I'm following \n>`/keywords` view keywords I'm searching for\n>`/add_user` add a Twitter account\n>`/add_keyword` add a keyword to search for\n>`/remove_user` remove a Twitter account\n>`/remove_keyword` remove a keyword search term\n>`/help` print help"
            }
        }
    ]
}

if __name__ == '__main__':
	res = client.views_publish(user_id=user_id, view=data, headers={"Content-type": "application/json"})
