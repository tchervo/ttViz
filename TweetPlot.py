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

# Loads tweets either from file (default) or from Twitter
def search_tweets(topic: str, load_tweets=True) -> list:
    tweet_text = []

    if load_tweets:
        tweet_text = dm.load_tweets(topic=topic)
    else:
        print("Loading Twitter!")
        tweets = tw.Cursor(api.search, q=topic).items(50)

        for tweet in tweets:
            tweet_text.append(tweet.text)

    return tweet_text


def do_stats(frame: pd.DataFrame):
    total_word_sum = sci.sum(frame["Freq"])
    target_word_sum = frame.iloc[0, 1]

    print(target_word_sum)

    print(str(total_word_sum), '\n', str(target_word_sum), '\n', str(target_word_sum / total_word_sum))


def main():
    login(load_account_data())

    mode = int(input("Select Mode (1 - Frequency | 2 - Association): "))
    should_save = input("Save tweets?: ")
    search = input("Input search term: ")

    if should_save.lower() == "yes":
        if len(search.split(",")) >= 2:
            for term in search.split(","):
                dm.save_tweets(topic=term)

                tweets = search_tweets(topic=term, load_tweets=True)
                data = dm.strip_tweet(tweets)
                frame = None

                if mode == 1:
                    frame = dm.build_dataframe(data)
                elif mode == 2:
                    frame = dm.build_dataframe(data)
        else:
            dm.save_tweets(topic=search)

            tweets = search_tweets(topic=search, load_tweets=True)
            data = dm.strip_tweet(tweets)
            frame = None

            if mode == 1:
                frame = dm.build_dataframe(data)
            elif mode == 2:
                frame = dm.build_dataframe(data)
    else:
        if len(search.split(",")) >= 2:
            for term in search.split(','):
                tweets = search_tweets(topic=term, load_tweets=True)
                data = dm.strip_tweet(tweets)
                frame = None
                if mode == 1:
                    frame = dm.build_dataframe(data)
                elif mode == 2:
                    frame = dm.build_dataframe(data)
                else:
                    pass
        else:
            tweets = search_tweets(topic=search, load_tweets=True)
            data = dm.strip_tweet(tweets)
            frame = None
            if mode == 1:
                frame = dm.build_dataframe(data)
            elif mode == 2:
                frame = dm.build_dataframe(data)
            else:
                pass

    print(frame.head(30))
    # do_stats(frame)

    if input("Run again?: ").capitalize() == "Y":
        main()
    else:
        print("Exiting...")


if __name__ == '__main__':
    main()
