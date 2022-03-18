import praw
from datetime import datetime
import pandas as pd


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

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        password=password,
        user_agent=user_agent,
        username=username,
    )
    return reddit


def read_inbox(reddit):
    for message in reddit.inbox.unread():
        if str(message.subject).lower() == 'discord':
            user = message.author
            ## TO-DO ##
            # if user.name = discord sent username
            # Check db for existing account and statistics for username
            # If it passes the test
            # mark read
            print(message.body)
            search_user_constraints(user)
            message.mark_read()
        else:
            message.mark_read()


def search_user_constraints(user):
    # Getting total karma
    total_karma = int(user.link_karma) + int(user.comment_karma)

    # Checking total karma constraint
    if total_karma > 1000:
        print("More than 1k karma")
    else:
        print("Less than 1k karma")

    # Checking account created more than 6 months ago constraint
    # 180days = 6 months
    date_created = datetime.fromtimestamp(user.created_utc)

    if abs(datetime.now() - date_created).days > 180:
        print("Account older than 6 months")
    else:
        print("Account not older than 6 months")

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

    # TO-DO
    # If total_comments and total_submissions are > a number let the user in


def main():
    reddit = login()
    read_inbox(reddit)


if __name__ == '__main__':
    main()
