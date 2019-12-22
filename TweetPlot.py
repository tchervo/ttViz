import os
import unicodedata

import pandas as pd
import scipy as sci
import tweepy as tw
import datamanager as dm

consumer_key = str(os.getenv("CONSUMER_KEY"))
consumer_secret = str(os.getenv("CONSUMER_SECRET"))

access_token = str(os.getenv("ACCESS_TOKEN"))
access_secret = str(os.getenv("ACCESS_SECRET"))

auth = tw.OAuthHandler(consumer_key, consumer_secret)

api = tw.API(auth, wait_on_rate_limit=True)


def load_account_data() -> pd.DataFrame:
    data = None

    try:
        data = pd.read_csv("account_plot.csv")
    except IOError:
        print("Accounts file does not exist! Will create new one.")

    return data


def login(account_data: pd.DataFrame):
    if account_data is None or account_data.empty:
        try:
            redirect_url = auth.get_authorization_url()
            print("Log in with this link: " + redirect_url)
            verifier = input("Verification Code: ")
            auth.get_access_token(verifier=verifier)

            # String access token
            a_t = str(unicodedata.normalize('NFKD', auth.access_token).encode("ascii", "ignore"))

            # String access secret
            a_s = str(unicodedata.normalize('NFKD', auth.access_token_secret).encode("ascii", "ignore"))

            account_data = pd.DataFrame(data={"access_token": a_t, "access_secret": a_s}, index=["value"])
            pd.DataFrame(account_data).to_csv("account_plot.csv")
        except tw.TweepError or IOError:
            print("An error occurred during authorization!")
    else:
        a_t = str(account_data.iat[0, 1]).replace('b', '', 1).replace("'", "")
        a_s = str(account_data.iat[0, 2]).replace('b', '', 1).replace("'", "")

        auth.set_access_token(a_t, a_s)


# # Loads tweets either from file (default) or from Twitter - Currently unused
# def search_tweets(topic: str, load_tweets=True) -> list:
#     tweet_text = []
#
#     if load_tweets:
#         tweet_text = dm.load_tweets(topic)
#     else:
#         print("Loading Twitter!")
#         print(topic)
#         tweets = tw.Cursor(api.search, q=topic).items(100)
#
#         for tweet in tweets:
#             tweet_text.append(tweet.text)
#
#     print(len(tweet_text))
#     return tweet_text

def main():
    account_data = load_account_data()
    login(account_data)

    mode = input("Select search mode: Topic (1), User (2), or Network (3): ")

    if mode == '1':
        topic = input("Select a topic to search: ")
        dm.save_tweets(topic)
        topic_file = dm.make_file_name_for_search(topic)
        topic_frame = dm.get_dataframe_from_file(topic_file)

        print(topic_frame.head())
        print(topic_frame.tail())
    elif mode == '2':
        username = input("Input username: ")
        dm.save_tweets(topic=username, do_search=False, to_save=dm.get_tweets_for_user(username))
    elif mode == '3':
        username = input("Input username: ")
        dm.search_network(username)
    else:
        print('Invalid input!')
        main()

    if input("Run again?: ").capitalize().startswith('Y'):
        main()
    else:
        print("Exiting...")

if __name__ == '__main__':
    main()
