import csv
import yaml
from pathlib import Path

try:
    config = yaml.safe_load(open('config.yaml'))
except yaml.YAMLError as exc:
    print(exc)

keyword_file = config['keyword_file']
user_file = config['user_file']

def get_keywords(file=keyword_file):
    """Return a list of Twitter topics the bot is following"""

    if not Path(file).exists():
        with open(file, "w") as my_empty_csv:
          pass  

    with open(file, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\n')
        keywords = []
        for row in spamreader:
            for item in row:
                keywords.append(item)
    return list(filter(lambda a: a != '', keywords))

def add_keyword(keyword, file=keyword_file):
    """Add a Twitter keyword to the keyword.csv file to follow"""
    keywords = get_keywords(file)
    if keyword not in keywords:
        with open(file, 'a') as csvfile:    
            spamwriter = csv.writer(csvfile)
            spamwriter.writerow([keyword])

def remove_keyword(keyword, file=keyword_file):
    """Add a Twitter user to follow file"""
    keywords = get_keywords(file)
    if keyword in keywords:
        keywords.remove(keyword)
        # write new keyword file
        with open(file, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='\n')
            for k in keywords:
                spamwriter.writerow([k])

def get_users(file=user_file):
    """Return a list of Twitter users the bot is following"""

    if not Path(file).exists():
        with open(file, "w") as my_empty_csv:
          pass

    with open(file, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\n')
        users = []
        for row in spamreader:
            for item in row:
                users.append(item)
    return list(filter(lambda a: a != '', users))

def add_user(user, file=user_file):
    """Add a Twitter user to the CSV file to follow"""
    users = get_users(file)
    if user not in users:
        with open(file, 'a') as csvfile:    
            spamwriter = csv.writer(csvfile)
            spamwriter.writerow([user])

def remove_user(user, file=user_file):
    """Add a Twitter user to follow file"""
    users = get_users(file)
    if user in users:
        users.remove(user)
        # write new user file
        with open(file, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter='\n')
            for u in users:
                spamwriter.writerow([u])
