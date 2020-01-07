import os

import nltk
import pandas as pd
from nltk.tokenize.casual import TweetTokenizer

import tweetplot

tw = tweetplot.tw
api = tweetplot.api


def make_file_name_for_search(search: str, type='tweets') -> str:
    """
    Generates a file name in the search_terms_type.csv format
    :param search: The name of the query. Can also be the desired name of the file
    :param type: The type of data in this search. Is appended as _type to the end of the file.
    :return: The path to the file as a string
    """

    search_dir = os.getcwd() + f'/{search}/'

    if os.path.exists(search_dir) is False:
        try:
            os.mkdir(search_dir)
        except IOError:
            print('Could not create directory: ' + search_dir)

    save_file = ''

    if len(search.split(',')) >= 2:
        for topic in search.split(','):
            if len(topic.split(' ')) >= 2:
                for word in topic.split(' '):
                    if save_file == '':
                        save_file = search_dir + word.lower()
                    else:
                        save_file = save_file + f'_{word.lower()}'
                save_file = save_file + '_{0}.csv'.format(type)
            else:
                save_file = '{0}_{1}.csv'.format(search.lower(), type)

    else:
        if len(search.split(' ')) >= 2:
            for word in search.split(' '):
                if save_file == '':
                    save_file = search_dir + word.lower()
                else:
                    save_file = save_file + f'_{word.lower()}'
            save_file = save_file + '_{0}.csv'.format(type)
        else:
            save_file = search_dir + '{0}_{1}.csv'.format(search.lower(), type)

    return save_file


def save_tweets(topic: str, do_search=True, to_save=[]):
    """
    Saves tweets to a CSV file named after their topic
    :param topic: The topic to search if needed. Also becomes the save name for the file
    :param do_search: Whether or not this function should search twitter first. Default is True
    :param to_save: An array of tweets to save if do_search is False.
    :return:
    """

    tweet_text = []
    tweet_ids = []
    tweet_favorites = []
    tweet_retweets = []
    tweet_screen_names = []
    tweet_times = []
    save_file = make_file_name_for_search(topic)

    if do_search:
        tweets = tw.Cursor(api.search, q=topic + ' -filter:retweets', lang='en', result_type='mixed').items(200)

        for tweet in tweets:
            if tweet.user.protected is not True:
                tweet_text.append(tweet.text)
                tweet_ids.append(tweet.id)
                tweet_favorites.append(int(tweet.favorite_count))
                tweet_retweets.append(int(tweet.retweet_count))
                tweet_screen_names.append(tweet.user.screen_name)
                tweet_times.append(str(tweet.created_at))

        tweet_frame = pd.DataFrame(data={'tweet_ID': tweet_ids, 'text': tweet_text, 'favorites': tweet_favorites,
                                         'retweets': tweet_retweets, 'screen_name': tweet_screen_names,
                                         'tweet_times': tweet_times})
        tweet_frame.to_csv(save_file)
    else:
        for tweet in to_save:
            tweet_text.append(tweet.text)
            tweet_ids.append(tweet.id)
            tweet_favorites.append(int(tweet.favorite_count))
            tweet_retweets.append(int(tweet.retweet_count))
            tweet_screen_names.append(tweet.user.screen_name)
            tweet_times.append(str(tweet.created_at))

        tweet_frame = pd.DataFrame(data={'tweet_ID': tweet_ids, 'text': tweet_text, 'favorites': tweet_favorites,
                                         'retweets': tweet_retweets, 'screen_name': tweet_screen_names,
                                         'tweet_times': tweet_times})
        print(tweet_frame)
        tweet_frame.to_csv(save_file)


def load_tweets(topic: str, from_file=True, frame=pd.DataFrame) -> [str]:
    """
    Loads tweets from CSV and returns an array of the tweets' text
    :param topic: Name of the file without .csv
    :param from_file: Whether the tweets should be loaded from a file. Default True
    :param frame: The dataframe to load the tweets from if from_file is False
    :return: An array of the tweet's text as a string
    """

    tweet_text = []
    file_name = make_file_name_for_search(topic)

    if from_file:
        tweet_frame = get_dataframe_from_file(file_name)

        for text in tweet_frame.text:
            tweet_text.append(text)
    else:
        for text in frame.text:
            tweet_text.append(text)

    return tweet_text


def get_dataframe_from_file(file_name: str) -> pd.DataFrame:
    """
    Tries to create a pandas dataframe from a CSV file path.
    :param file_name: The path of the file to be loaded.
    :return: A pandas dataframe containing the information in the CSV file
    """

    ret_frame = None

    try:
        ret_frame = pd.read_csv(file_name)
    except IOError as error:
        print(f'An error occured loading dataframe with name: {file_name}! (Wrong name?)')
        print(error)

    return ret_frame


def get_tweets_for_user(username: str, filter_retweets=True) -> []:
    """
    Gets 100 tweets from the user's profile, optionally filtering for retweets.
    :param username: The screen name of the desired user. Can also be other user identifiers
    :param filter_retweets: Whether or not retweets should be filtered. Default is True
    :return: An array of the tweets appearing on the user's profile
    """

    user = None
    tweets = []

    try:
        user = api.get_user(username, tweet_mode='extended')
    except tw.TweepError as error:
        print(f'Could not find user with username: {username} because {error.reason}')
        print(error.api_code)
        tweetplot.repeat_menu()

    if user.protected is not True:
        if filter_retweets:
            for tweet in api.user_timeline(user.id, count=100):
                if str(tweet.text).startswith('RT') is False:
                    tweets.append(tweet)

            return tweets
        else:
            return api.user_timeline(user.id, count=100)
    else:
        print(f'{username} has a private account!')
        return 'PRIVATE'


def build_frequency_frame(data: []) -> pd.DataFrame:
    """
    Assembles a pandas dataframe out of the frequency of specific words.
    :param data: A list of words
    :return: A dataframe with columns 'word' and 'freq' containg the word and its frequency
    """

    word_counter = {}
    word_list = []
    freq_list = []

    for word in data:

        if word in word_counter.keys():
            new_count = int(word_counter[word]) + 1
            word_counter[word] = new_count
        else:
            # Accounts for capitalization variations
            word_counter[word.lower()] = 1

    for word in word_counter.keys():
        word_list.append(word)
    for freq in word_counter.values():
        freq_list.append(freq)

    ret_frame = pd.DataFrame({'word': word_list, 'freq': freq_list}).sort_values(by=['freq'], ascending=False)

    return ret_frame


# Removes 'RT' and '#' from tweets and selects for meaningful words - Currently unused
# def strip_tweets(whole_tweet_list: str) -> [str]:
#     stripped_tweet = []
#
#     for whole_tweet in whole_tweet_list:
#         for phrase in whole_tweet.split(' '):
#             if phrase == 'RT' or phrase.startswith('@') or phrase.startswith(' ') or phrase.isalnum() is not True:
#                 phrase = 'pass'
#             else:
#                 if phrase.lower() in stopwords.words('english'):
#                     phrase = 'pass'
#             if phrase != 'pass':
#
#                 stripped_tweet.append(phrase.encode('utf-8'))
#
#     return stripped_tweet


def search_network(root_user: str, should_save=True) -> pd.DataFrame:
    """
    Searches for a user, then selects 100 of that user's followers and builds a frequency map
    :param root_user: An identifier for the user whose followers should be searched as well
    :param should_save: Should the tweets be saved to a .csv file. Default is True
    :return: A frequency frame [See datamanager.build_frequency_frame()] for the network
    """

    network_ids = []
    network_tweets = []

    try:
        user = api.get_user(root_user, tweet_mode='extended')
    except tw.TweepError as error:
        print(f'Could not find user with username: {root_user} because {error.reason}')
        print(error.api_code)
        tweetplot.repeat_menu()

    network_ids.append(user.id)

    for follower_id in tw.Cursor(api.followers_ids, id=root_user).items(100):
        try:
            follower = api.get_user(follower_id)
        except tw.TweepError as error:
            print(f'An error occurred trying to find follower with ID: {follower_id} because {error.reason}')

        if follower.protected is not True:
            network_ids.append(follower_id)

    for id_ in network_ids:
        net_user_tl = api.user_timeline(id_)

        for tweet in net_user_tl:
            if str(tweet.text).startswith('RT') is False:
                network_tweets.append(tweet.text)

    network_words = select_nouns(network_tweets)
    network_frame = build_frequency_frame(network_words)

    if should_save:
        network_frame.to_csv(make_file_name_for_search(search=root_user, type='network'))

    return network_frame


def screen_names_from_ids(id_list: []) -> [str]:
    """
    Takes a list of user IDs and turns them into screen names
    :param id_list: A list of user IDs to process
    :return: A list of user screen names
    """

    name_list = []

    for user_id in id_list:
        try:
            user = api.get_user(user_id)

            if user.protected is not True:
                name_list.append(user.screen_name)
        except tw.TweepError as error:
            print(f'Could not find user with ID: {user_id} because {error.reason}')
            print(error.api_code)

    return name_list


def build_user_frame(identifier: str) -> pd.DataFrame:
    """
    Creates a pandas dataframe that contains all of the tweets, retweets, and up to 100 liked tweets for a user.
    :param identifier: An identifier such as a screen name or ID for the user
    :return: A dataframe containing the user's tweets, retweets, and liked tweets
    """

    tl_tweets = get_tweets_for_user(identifier, filter_retweets=False)
    favorited_tweets = tw.Cursor(api.favorites, id=identifier).items(100)

    tweet_text = []
    tweet_ids = []
    tweet_screen_names = []

    for tweet in tl_tweets:
        tweet_text.append(tweet.text)
        tweet_ids.append(tweet.id)
        tweet_screen_names.append(tweet.user.screen_name)
    for tweet in favorited_tweets:
        tweet_text.append(tweet.text)
        tweet_ids.append(tweet.id)
        tweet_screen_names.append(tweet.user.screen_name)

    frame_data = {'tweet_id': tweet_ids, 'text': tweet_text, 'screen_name': tweet_screen_names}
    ret_frame = pd.DataFrame(frame_data)

    ret_frame.to_csv(make_file_name_for_search(identifier))

    return ret_frame


def select_nouns(tweets: []) -> [str]:
    """
    Selects all of the nouns out of a user's tweets
    :param tweets: An array of tweets to process
    :return: A list of nouns used in the provided tweets
    """

    nouns = []
    tweet_tokenizer = TweetTokenizer()

    for text in tweets:
        token_sentences = tweet_tokenizer.tokenize(text)

        for sentence in token_sentences:
            words = nltk.word_tokenize(str(sentence))
            for word, code in nltk.pos_tag(words):
                if code.startswith('NN') and word.isalnum() and len(word) > 1 and word != 'https':
                    nouns.append(word)

    return nouns

