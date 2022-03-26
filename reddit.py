# import praw
import asyncpraw
from datetime import datetime
import pandas as pd
from enums import ReturnType
from collections import defaultdict


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


client_id, client_secret, password, user_agent, username = read_csv()


# def login():
#     # Read authentication data from the .csv file
#     client_id, client_secret, password, user_agent, username = read_csv()
#     try:
#         reddit = praw.Reddit(
#             client_id=client_id,
#             client_secret=client_secret,
#             password=password,
#             user_agent=user_agent,
#             username=username,
#         )
#         return reddit
#     except Exception as e:
#         print("Error while trying to login to reddit.")
#         print(e)
#         return None


def stats_view(user_dict, six_mos, mode):
    keys = user_dict.keys()
    vals = user_dict.values()

    v, k = zip(*sorted((zip(vals, keys)), reverse=True))

    total = sum(vals)
    stats = "```"
    # print('From the last ', total, mode)
    # print('{:<20}| Percentage | Number | 6 Months'.format("Subreddit"))
    # print('-----------------------------------------------------')
    stats += f'From the last {total} {mode}\n'
    stats += '{:<20}| Percentage | Number | 6 Months\n'.format("Subreddit")
    stats += '-----------------------------------------------------\n'
    other_count = 0
    other_6_mos = 0
    for i in range(len(vals)):
        if i > 9:
            other_count += v[i]
            other_6_mos += six_mos[k[i]]
            continue
        # print("{:<20}| {:<10} | {:<6} | {} ".format(k[i], str(v[i]/total*100)+"%", v[i], six_mos[k[i]]))
        stats += "{:<20}| {:<10} | {:<6} | {} \n".format(k[i], str(v[i] / total * 100) + "%", v[i], six_mos[k[i]])

    if len(vals) > 10:
        # print("{:<20}| {:<10} | {:<6} | {} ".format('Other Subreddits', str(other_count/ total * 100) + "%", other_count, other_6_mos))
        stats += "{:<20}| {:<10} | {:<6} | {} \n".format('Other Subreddits', str(other_count / total * 100) + "%",
                                                         other_count, other_6_mos)
    stats += '```'

    return stats


# def read_inbox(reddit, discord_sent_username):
#     reddit = asyncpraw.Reddit(
#         client_id=client_id,
#         client_secret=client_secret,
#         password=password,
#         user_agent=user_agent,
#         username=username,
#     )
#
#
#     for message in reddit.inbox.unread():
#         if str(message.subject).lower() == 'discord':
#             user = message.author
#             ## TO-DO ##
#             # Check db for existing account
#
#             # Checks that the reddit user is equal to the message from discord
#             if str(user).lower() == discord_sent_username:
#                 print("Now searching user: ", user)
#                 message.mark_read()
#                 # Search the constraints
#                 return search_user_constraints(user)
#             else:
#                 # If there usernames sent don't match and don't mark message as read
#                 return ReturnType.NoSuchUsername
#
#         else:
#             # Mark message as read and return the NoSuchUsername type
#             message.mark_read()
#             return ReturnType.NoSuchUsername
#
#     # If code reaches here it means no message with subject 'Discord' is found
#     return ReturnType.NoSuchUsername


async def search_user_stats(user):
    # print(f'Redditor: {user.name}')
    # print(f'Suspended?: {user.is_suspended}')
    # Getting total karma
    total_karma = int(user.link_karma) + int(user.comment_karma)
    summary = []
    determination_flags = defaultdict(int)
    summary.append(f"__**Summary for user /r/{user.name}**__.\n<https://reddit.com/r/{user.name}>")
    # Checking total karma constraint
    # if total_karma > 1000:
    #     print("More than 1k karma")
    # else:
    #     print("Less than 1k karma")
    summary.append(f"The user has {total_karma} karma.")

    print(summary[-1])  # debug

    determination_flags["karma"] = int(total_karma > 1000)

    # Checking account created more than 6 months ago constraint
    # 180days = 6 months
    date_created = datetime.fromtimestamp(user.created_utc)

    if abs(datetime.now() - date_created).days > 180:
        summary.append("The account is older than 6 months")
    else:
        print("The account is **NOT** older than 6 months")
        # return ReturnType.Declined

    print(summary[-1])
    determination_flags['age'] = int(abs(datetime.now() - date_created).days > 180)

    # Get comments from 't5_2qh8i' -> /r/greece
    # comments = user.comments.new(limit=200)
    # print(comments)
    comment_count = defaultdict(int)
    comments_6mos = defaultdict(int)
    async for comment in user.comments.new(limit=200):
        comment_count[str(comment.subreddit.display_name.lower())] += 1

        if abs(datetime.fromtimestamp(comment.created_utc) - datetime.now()).days < 180:
            comments_6mos[str(comment.subreddit.display_name.lower())] += 1

    # print(comment_count)
    summary.append(stats_view(comment_count, comments_6mos, "Comments"))
    print(summary[-1])

    submission_count = defaultdict(int)
    # submissions = user.submissions.new(limit=200)
    submission_6mos = defaultdict(int)

    async for submission in user.submissions.new(limit=200):
        submission_count[str(submission.subreddit.display_name).lower()] += 1
        if abs(datetime.fromtimestamp(submission.created_utc) - datetime.now()).days < 180:
            submission_6mos[str(submission.subreddit.display_name).lower()] += 1

    summary.append(stats_view(submission_count, submission_6mos, "Submissions"))
    print(summary[-1])

    total_comments = comment_count['greece']
    total_submissions = submission_count['greece']

    summary.append(f'Total comments from /r/greece: {total_comments}')
    summary.append(f'Total submissions from /r/greece: {total_submissions}')
    print(summary[-1])
    print(summary[-2])

    # TODO: check if user is banned

    # if any(reddit.subreddit('greece').banned(redditor=user.name)):
    #     print("The user is banned from /r/greece for ", reddit.subreddit('greece').banned(redditor=user.name).note)

    # TODO: check if user is Suspended

    # TODO: Usernotes: follow this link to do usernotes in the future https://www.reddit.com/r/toolbox/comments/6y40rz/decompressing_the_usernotes_in_a_praw_script/

    # TODO: Blacklist. Read from a file that has a blacklisted subreddit on each line. If in blacklist view participation in table

    # if total_comments < 20 or total_submissions < 5:
    #     return ReturnType.Declined

    determination_flags['participation'] = int(total_comments < 20 or total_submissions < 5)
    return summary


def search_user(discord_sent_username):
    reddit = login()
    if reddit is not None:
        # read inbox
        return read_inbox(reddit, discord_sent_username)
