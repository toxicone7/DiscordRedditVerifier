import praw
#import asyncpraw
from datetime import datetime
import pandas as pd
from enums import ReturnType


def read_csv():
    # Read authentication data from the .csv file
    try:
        values = pd.read_csv('creds.csv', delimiter=';')
        client_id = values['client_id'].iloc[0]
        client_secret = values['client_secret'].iloc[0]
        password = values['password'].iloc[0]
        user_agent = values['user_agent'].iloc[0]
        username = values['username'].iloc[0]
        return client_id, client_secret, password, user_agent, username
    except FileNotFoundError as e:
        print("Not found the creds.csv file.")
        print(e)
    except Exception as e:
        print(e)


def login():
    # Read authentication data from the .csv file
    client_id, client_secret, password, user_agent, username = read_csv()
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            password=password,
            user_agent=user_agent,
            username=username,
        )
        return reddit
    except Exception as e:
        print("Error while trying to login to reddit.")
        print(e)
        return None


def read_inbox(reddit, discord_sent_username):
    for message in reddit.inbox.unread():
        if str(message.subject).lower() == 'discord':
            user = message.author
            ## TO-DO ##
            # Check db for existing account

            # Checks that the reddit user is equal to the message from discord
            if str(user).lower() == discord_sent_username:
                print("Now searching user: ", user)
                message.mark_read()
                # Search the constraints
                return search_user_constraints(user)
            else:
                # If there usernames sent don't match and don't mark message as read
                return ReturnType.NoSuchUsername

        else:
            # Mark message as read and return the NoSuchUsername type
            message.mark_read()
            return ReturnType.NoSuchUsername

    # If code reaches here it means no message with subject 'Discord' is found
    return ReturnType.NoSuchUsername


def search_user_constraints(user):
    # Getting total karma
    total_karma = int(user.link_karma) + int(user.comment_karma)

    # Checking total karma constraint
    if total_karma > 1000:
        print("More than 1k karma")
    else:
        print("Less than 1k karma")
        return ReturnType.Declined

    # Checking account created more than 6 months ago constraint
    # 180days = 6 months
    date_created = datetime.fromtimestamp(user.created_utc)

    if abs(datetime.now() - date_created).days > 180:
        print("Account older than 6 months")
    else:
        print("Account not older than 6 months")
        return ReturnType.Declined

    # Get comments from 't5_2qh8i' -> /r/greece
    total_comments = 0
    comments = user.new(limit=100)
    for comment in comments:
        if comment.subreddit_id == 't5_2qh8i':
            total_comments += 1
        else:
            continue
            # comment not from /r/greece

    # Get submissions from 't5_2qh8i' -> /r/greece
    total_submissions = 0
    submissions = user.submissions.new(limit=100)
    for submission in submissions:
        if submission.subreddit_id == 't5_2qh8i':
            total_submissions += 1
        else:
            # submission not from /r/greece
            continue

    print("Total comments from /r/greece: ", total_comments)
    print("Total submissions from /r/greece: ", total_submissions)

    if total_comments < 20 or total_submissions < 5:
        return ReturnType.Declined

    return ReturnType.Accepted


def search_user(discord_sent_username):
    reddit = login()
    if reddit is not None:
        # read inbox
        return read_inbox(reddit, discord_sent_username)