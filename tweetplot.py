import os
import unicodedata

import pandas as pd
import tweepy as tw

import datamanager as dm
import plotmaker as plotter

consumer_key = str(os.getenv('CONSUMER_KEY'))
consumer_secret = str(os.getenv('CONSUMER_SECRET'))

access_token = str(os.getenv('ACCESS_TOKEN'))
access_secret = str(os.getenv('ACCESS_SECRET'))

auth = tw.OAuthHandler(consumer_key, consumer_secret)

api = tw.API(auth, wait_on_rate_limit=True)


# Loads account data from account_plot.csv
def load_account_data() -> pd.DataFrame:
    data = None

    try:
        data = pd.read_csv('account_plot.csv')
    except IOError:
        print('Accounts file does not exist! Will create new one.')

    return data


# Logs in to Twitter, requesting that the user authorizes the app if needed
def login(account_data: pd.DataFrame):
    if account_data is None or account_data.empty:
        try:
            redirect_url = auth.get_authorization_url()
            print('Log in with this link: ' + redirect_url)
            verifier = input('Verification Code: ')
            auth.get_access_token(verifier=verifier)

            # String access token
            a_t = str(unicodedata.normalize('NFKD', auth.access_token).encode('ascii', 'ignore'))

            # String access secret
            a_s = str(unicodedata.normalize('NFKD', auth.access_token_secret).encode('ascii', 'ignore'))

            account_data = pd.DataFrame(data={'access_token': a_t, 'access_secret': a_s}, index=['value'])
            pd.DataFrame(account_data).to_csv('account_plot.csv')
        except tw.TweepError or IOError:
            print('An error occurred during authorization!')
            repeat_menu()
    else:
        a_t = str(account_data.iat[0, 1]).replace('b', '', 1).replace("'", '')
        a_s = str(account_data.iat[0, 2]).replace('b', '', 1).replace("'", '')

        auth.set_access_token(a_t, a_s)


# Asks the user if the software should be ran again
def repeat_menu():
    if input('Run again?: ').capitalize().startswith('Y'):
        main()
    else:
        print('Exiting...')


def main():
    account_data = load_account_data()
    login(account_data)

    mode = input('Select search mode: Topic (1), User (2), or Network (3): ')
    should_plot = input('Plot results?: ').lower().startswith('y') is True

    if mode == '1':
        topic = input('Select a topic to search: ')
        dm.save_tweets(topic)
        topic_file = dm.make_file_name_for_search(topic)
        topic_frame = dm.get_dataframe_from_file(topic_file)

        topics_tweets = dm.load_tweets(topic=topic, from_file=False, frame=topic_frame)
        topic_tweets_stripped = dm.strip_tweets(topics_tweets)
        freq_file_name = dm.make_file_name_for_search(topic, type='freq')
        topic_tweets_frame = dm.build_frequency_frame(topic_tweets_stripped)

        topic_tweets_frame.to_csv(freq_file_name)

        plot_tweets = topic_tweets_frame[topic_tweets_frame.freq >= 3]

        if should_plot:
            plotter.build_bar_plot(plot_tweets, 'word', 'freq', topic)

    elif mode == '2':
        username = input('Input username: ')
        user_tweets = dm.get_tweets_for_user(username)
        dm.save_tweets(topic=username, do_search=False, to_save=user_tweets)
        ut_frame = pd.read_csv(dm.make_file_name_for_search(username))

        if should_plot:
            plotter.build_scatter_plot(ut_frame, 'favorites', 'retweets', f'@{username}')
    elif mode == '3':
        username = input('Input username: ')
        dm.search_network(username)
    else:
        print('Invalid input!')
        main()

    repeat_menu()


if __name__ == '__main__':
    main()
