import logging
import os
import unicodedata

import pandas as pd
import tweepy as tw

import datamanager as dm
import statsmanager as sm
from plotmaker import PlotMaker

consumer_key = str(os.getenv('CONSUMER_KEY'))
consumer_secret = str(os.getenv('CONSUMER_SECRET'))

access_token = str(os.getenv('ACCESS_TOKEN'))
access_secret = str(os.getenv('ACCESS_SECRET'))

auth = tw.OAuthHandler(consumer_key, consumer_secret)

api = tw.API(auth, wait_on_rate_limit=True)

log_path = os.getcwd() + '/logs/ttViz_log.log'
log_format = '%(levelname)s | %(asctime)s | %(message)s'

if os.path.exists(os.getcwd() + '/logs/') is not True:
    try:
        os.mkdir("logs")
    except IOError as error:
        print(f'Could not create log directory {os.getcwd()}/logs/ ! Logging info will be unavailable!')

logging.basicConfig(filename=log_path, level=logging.DEBUG, filemode='w', format=log_format)

logger = logging.getLogger()


def load_account_data() -> pd.DataFrame:
    """
    Loads account data from account_plot.csv
    :return: A dataframe containing the account access token and secret if it exists. None otherwise
    """

    data = None

    try:
        data = pd.read_csv('account_plot.csv')
    except IOError:
        print('Accounts file does not exist! Will create new one.')
        logger.info('Could not find account data file! Creating new one...')

    return data


def login(account_data: pd.DataFrame):
    """
    Logs in to Twitter, requesting that the user authorizes the app if needed
    :param account_data: Dataframe with the account access token and secret. Can be None
    """

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
            logger.critical('Could not access user account!')
    else:
        a_t = str(account_data.iat[0, 1]).replace('b', '', 1).replace("'", '')
        a_s = str(account_data.iat[0, 2]).replace('b', '', 1).replace("'", '')

        auth.set_access_token(a_t, a_s)


def make_path_for_image(image_topic: str) -> str:
    """
    Creates a path to an image to be posted
    :param image_topic: The name of the image without _plot.png
    :return: A string of the file path for the plot image
    """

    file_name = os.getcwd() + '/' + image_topic + '/' + image_topic.lower().replace(' ', '_') + '_plot.png'

    return file_name


def post_tweet(text: str, with_image=True, image_name=''):
    """
    Post a tweet to the currently authenticated account
    :param text: The text of the post to be made
    :param with_image: Should this post include an image? Defaults to True
    :param image_name: Path to the image file
    """

    image_path = make_path_for_image(image_name)

    if with_image:
        api.update_with_media(image_path, status=text)
    else:
        try:
            api.update_status(status=text)
        except tw.TweepError as error:
            print(f'Could not update user status because {error.response}')
            logger.error(f'Could not update status because {error.response}')


def repeat_menu():
    """
    Asks the user if the software should be ran again
    """

    if input('Run again?: ').capitalize().startswith('Y'):
        main()
    else:
        print('Exiting...')


def process_command(command: str, args=[]):
    """
    Handles incoming user commands
    :param command: A string indicating the command type. Valid types are topic, user, network, tweet
    :param args: Any additional information required to execute the command. Optional
    :return: Varies by command
    """

    if command == 'topic':
        topic = input('Select a topic to search: ')
        save_name = topic
        assigned_name = args[1]
        tweet_limit = input('Input the maximum number of tweets to get (Leave blank for 100): ')

        if tweet_limit != '':
            try:
                tweet_limit = int(tweet_limit)

                if tweet_limit < 1:
                    print(f'Input {tweet_limit} is too low! Defaulting to 100')
                    tweet_limit = 100
            except ValueError:
                print(f'Invalid input {tweet_limit}! Defaulting to 100')
                tweet_limit = 100
        else:
            tweet_limit = 100

        if assigned_name != '':
            save_name = assigned_name

        topics_tweets_whole = dm.search_tweets_for_query(query=topic, limit=tweet_limit)
        dm.save_tweets(save_name, to_save=topics_tweets_whole)
        topic_tweets_text = dm.load_tweet_text(topic)
        should_plot = args[0]

        topic_tweets_stripped = dm.select_pos_words(topic_tweets_text)
        freq_file_name = dm.make_file_name_for_search(save_name, type='freq')
        topic_tweets_frame = dm.build_frequency_frame(topic_tweets_stripped)

        topic_tweets_frame.to_csv(freq_file_name)

        plot_tweets = topic_tweets_frame[topic_tweets_frame.freq >= 3]
        plotter = PlotMaker(f'Frequency of Words Used When Tweeting About {save_name.title()}', plot_tweets)

        if should_plot:
            plotter.build_bar_plot('word', 'freq', topic)

    elif command == 'user':
        username = input('Input username: ')
        user_tweets = dm.get_tweets_for_user(username)
        user_mode = args[0]
        should_plot = args[1]

        if user_mode == '1':
            user_frame = dm.build_user_frame(username)
            whole_tweets = dm.load_tweet_text(username, from_file=False, frame=user_frame)
            stripped_tweets = dm.select_pos_words(whole_tweets)
            freq_frame = dm.build_frequency_frame(stripped_tweets)
        elif user_mode == '2':
            dm.save_tweets(username, to_save=user_tweets)
            tweet_text = dm.load_tweet_text(username)
            stripped_text = dm.select_pos_words(tweet_text)
            user_tweet_frame = dm.build_frequency_frame(stripped_text)
            user_tweet_frame = user_tweet_frame[user_tweet_frame.freq > 3]
        elif user_mode == '3':
            dm.save_tweets(username, to_save=user_tweets)
            ut_frame = pd.read_csv(dm.make_file_name_for_search(username))

        if should_plot:
            if user_mode == '1':
                title = f'Frequency of Words on {username}s profile'
                plotter = PlotMaker(title, freq_frame)
                plotter.build_bar_plot('word', 'freq', username)
            elif user_mode == '2':
                title = f'Frequency of Words in {username}s tweets'
                plotter = PlotMaker(title, user_tweet_frame)
                plotter.build_bar_plot('word', 'freq', f'{username}s tweets')
            elif user_mode == '3':
                title = f'Retweets as a function of favorites for {username}'
                plotter = PlotMaker(title, ut_frame)
                plotter.build_scatter_plot('favorites', 'retweets', username)
    elif command == 'network':
        username = input('Input username: ')
        net_frame = dm.search_network(username)
        should_plot = args[0]
        plotter = PlotMaker(f'Frequency of Words in {username}s network', net_frame)

        if should_plot:
            plotter.build_bar_plot('word', 'freq', username)
    elif command == 'tweet':
        post_text = input('Entire the text for your post: ')
        graph_name = input('Select a graph to post: ')

        if len(post_text) > 280:
            print('Post is too long! Try again')
        else:
            post_tweet(post_text, image_name=graph_name)
    else:
        print(f'Unknown command: {command}')


def main():
    account_data = load_account_data()
    login(account_data)

    mode = input('Select search mode: Topic (1), User (2), Network (3), post a tweet (4), or do test stats (5): ')
    should_plot = input('Plot results?: ').lower().startswith('y') is True

    if mode == '1':
        assigned_name = input('Assign a unique name to this search? (Blank for default): ')
        process_command('topic', [should_plot, assigned_name])

    elif mode == '2':
        user_mode = input('Entire profile (1), profile tweets (2), like/retweet relationship (3)?: ')

        process_command('user', [user_mode, should_plot])
    elif mode == '3':
        process_command('network', [should_plot])
    elif mode == '4':
        process_command('tweet', args=[])
    elif mode == '5':
        user1 = input('Input first users username: ')
        user2 = input('Input second users username: ')

        user1_tweets = dm.get_tweets_for_user(user1)
        user2_tweets = dm.get_tweets_for_user(user2)

        dm.save_tweets(user1, to_save=user1_tweets)
        dm.save_tweets(user2, to_save=user2_tweets)

        user1_data = pd.read_csv(dm.make_file_name_for_search(user1))
        user2_data = pd.read_csv(dm.make_file_name_for_search(user2))

        fav_stat, fav_pval, rt_stat, rt_pval = sm.do_t_test(user1_data, user2_data)

        if should_plot:
            comb_data = [user1_data['favorites'], user1_data['retweets'], user2_data['favorites'],
                         user2_data['retweets']]

            box_plotter = PlotMaker(f'Distribution of Favorites and Retweets for @{user1} and @{user2}', comb_data)

            box_plotter.build_boxplot(f'{user1}_{user2}_comp', xlabels=[f'{user1} Favorites', f'{user1} Retweets',
                                                                        f'{user2} Favorites', f'{user2} Retweets'])

            fav_stat = round(fav_stat, 4)
            fav_pval = round(fav_pval, 4)
            rt_stat = round(rt_stat, 4)
            rt_pval = round(rt_pval, 4)

        test_tweet = sm.format_tweet_from_stats((fav_stat, fav_pval, rt_stat, rt_pval), opt_data=[user1, user2])
        print(test_tweet)
    else:
        print('Invalid input!')
        main()

    repeat_menu()


if __name__ == '__main__':
    main()
