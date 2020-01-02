import os
import unicodedata

import pandas as pd
import tweepy as tw

import datamanager as dm
from plotmaker import PlotMaker

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


# Creates a path to an image to be posted
def make_path_for_image(image_topic: str) -> str:
    image_dir = os.getcwd() + '/' + image_topic.lower().replace(' ', '_') + '/'
    image_filename = image_topic.lower().replace(' ', '_') + '.png'

    return image_dir + image_filename


# Post a tweet to the currently authenticated account
def post_tweet(text: str, with_image=True, image_name=''):
    image_path = make_path_for_image(image_name)

    if with_image:
        try:
            api.update_with_media(filename=image_path, status=text)
        except tw.TweepError as error:
            print(f'Could not update user status because {error.response}')
    else:
        try:
            api.update_status(status=text)
        except tw.TweepError as error:
            print(f'Could not update user status because {error.response}')


# Asks the user if the software should be ran again
def repeat_menu():
    if input('Run again?: ').capitalize().startswith('Y'):
        main()
    else:
        print('Exiting...')


# Handles incoming user commands
def process_command(command: str, args=[]):
    if command == 'topic':
        topic = input('Select a topic to search: ')
        dm.save_tweets(topic)
        topic_file = dm.make_file_name_for_search(topic)
        topic_frame = dm.get_dataframe_from_file(topic_file)
        should_plot = args[0]
        plotter = PlotMaker(f'Frequency of Words Used When Tweeting About {topic.capitalize()}')

        topics_tweets = dm.load_tweets(topic=topic, from_file=False, frame=topic_frame)
        topic_tweets_stripped = dm.strip_tweets(topics_tweets)
        freq_file_name = dm.make_file_name_for_search(topic, type='freq')
        topic_tweets_frame = dm.build_frequency_frame(topic_tweets_stripped)

        topic_tweets_frame.to_csv(freq_file_name)

        plot_tweets = topic_tweets_frame[topic_tweets_frame.freq >= 3]

        if should_plot:
            plotter.build_bar_plot(plot_tweets, 'word', 'freq', topic)
    elif command == 'user':
        username = input('Input username: ')
        user_tweets = dm.get_tweets_for_user(username)
        user_mode = args[0]
        should_plot = args[1]

        if user_mode == '1':
            user_frame = dm.build_user_frame(username)
            whole_tweets = dm.load_tweets(username, from_file=False, frame=user_frame)
            stripped_tweets = dm.strip_tweets(whole_tweets)
            freq_frame = dm.build_frequency_frame(stripped_tweets)
        elif user_mode == '2':
            dm.save_tweets(username, do_search=False, to_save=user_tweets)
            tweet_text = dm.load_tweets(username)
            stripped_text = dm.strip_tweets(tweet_text)
            user_tweet_frame = dm.build_frequency_frame(stripped_text)
            user_tweet_frame = user_tweet_frame[user_tweet_frame.freq > 3]
        elif user_mode == '3':
            dm.save_tweets(topic=username, do_search=False, to_save=user_tweets)
            ut_frame = pd.read_csv(dm.make_file_name_for_search(username))

        if should_plot:
            if user_mode == '1':
                plotter = PlotMaker(f'Frequency of Words on {username}s profile')
                plotter.build_bar_plot(freq_frame, 'word', 'freq', username)
            elif user_mode == '2':
                plotter = PlotMaker(f'Frequency of Words in {username}s tweets')
                plotter.build_bar_plot(user_tweet_frame, 'word', 'freq', f'{username}s tweets')
            elif user_mode == '3':
                plotter = PlotMaker(f'Retweets as a function of favorites for {username.capitalize()}')
                plotter.build_scatter_plot(ut_frame, 'favorites', 'retweets', username)
    elif command == 'network':
        username = input('Input username: ')
        net_frame = dm.search_network(username)
        should_plot = args[0]
        plotter = PlotMaker(f'Frequency of Words in {username}s network')

        if should_plot:
            plotter.build_bar_plot(net_frame, 'word', 'freq', username)
    else:
        print(f'Unknown command: {command}')


def main():
    account_data = load_account_data()
    login(account_data)

    mode = input('Select search mode: Topic (1), User (2), Network (3), or run tests (4): ')
    should_plot = input('Plot results?: ').lower().startswith('y') is True

    if mode == '1':
        process_command('topic', [should_plot])

    elif mode == '2':
        user_mode = input('Entire profile (1), profile tweets (2), like/retweet relationship (3)?: ')

        process_command('user', [user_mode, should_plot])
    elif mode == '3':
        process_command('network', [should_plot])
    elif mode == '4':
        pass
    else:
        print('Invalid input!')
        main()

    repeat_menu()


if __name__ == '__main__':
    main()
