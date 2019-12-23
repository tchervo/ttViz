import pandas as pd
from nltk.corpus import stopwords

import TweetPlot

tw = TweetPlot.tw
api = TweetPlot.api


def make_file_name_for_search(search: str, type='tweets') -> str:
    save_file = ''

    if len(search.split(',')) >= 2:
        for topic in search.split(','):
            if len(topic.split(' ')) >= 2:
                for word in topic.split(' '):
                    if save_file is '':
                        save_file = word.lower()
                    else:
                        save_file = save_file + f'_{word.lower()}'
                        print(save_file)
                save_file = save_file + '_{0}.csv'.format(type)
            else:
                save_file = '{0}_{1}.csv'.format(search.lower(), type)

    else:
        if len(search.split(' ')) >= 2:
            for word in search.split(' '):
                if save_file is '':
                    save_file = word.lower()
                else:
                    save_file = save_file + f'_{word.lower()}'
                    print(save_file)
            save_file = save_file + '_{0}.csv'.format(type)
        else:
            save_file = '{0}_{1}.csv'.format(search.lower(), type)

    return save_file


# Saves tweets to a CSV file named after their topic
def save_tweets(topic: str, do_search=True, to_save=[]):
    tweet_text = []
    tweet_ids = []
    tweet_favorites = []
    tweet_retweets = []
    tweet_screen_names = []
    tweet_times = []
    save_file = make_file_name_for_search(topic)

    if do_search:
        tweets = tw.Cursor(api.search, q=topic + ' -filter:retweets', lang="en", result_type='popular').items(100)

        for tweet in tweets:
            if bool(tweet.truncated):
                tweet_text.append(tweet.extended_tweet.full_text)
            else:
                tweet_text.append(tweet.text)

            tweet_ids.append(tweet.id)
            tweet_favorites.append(int(tweet.favorite_count))
            tweet_retweets.append(int(tweet.retweet_count))
            tweet_screen_names.append(tweet.user.screen_name)
            tweet_times.append(str(tweet.created_at))

        tweet_frame = pd.DataFrame(data={"tweet_ID": tweet_ids, "text": tweet_text, "favorites": tweet_favorites,
                                         "retweets": tweet_retweets, "screen_name": tweet_screen_names,
                                         "tweet_times": tweet_times})
        tweet_frame.to_csv(save_file)
    else:
        for tweet in to_save:
            tweet_text.append(tweet.text)
            tweet_ids.append(tweet.id)
            tweet_favorites.append(int(tweet.favorite_count))
            tweet_retweets.append(int(tweet.retweet_count))
            tweet_screen_names.append(tweet.user.screen_name)
            tweet_times.append(str(tweet.created_at))

        tweet_frame = pd.DataFrame(data={"tweet_ID": tweet_ids, "text": tweet_text, "favorites": tweet_favorites,
                                         "retweets": tweet_retweets, "screen_name": tweet_screen_names,
                                         "tweet_times": tweet_times})
        tweet_frame.to_csv(save_file)


# Loads tweets from CSV and returns an array of the tweets' text
def load_tweets(topic: str) -> [str]:
    tweet_text = []
    file_name = make_file_name_for_search(topic)

    tweet_frame = get_dataframe_from_file(file_name)

    for text in tweet_frame.text:
        tweet_text.append(text)

    return tweet_text


def get_dataframe_from_file(file_name: str) -> pd.DataFrame:
    ret_frame = None

    try:
        ret_frame = pd.read_csv(file_name)
    except IOError as error:
        print(f'An error occured loading dataframe with name: {file_name}! (Wrong name?)')
        print(error)

    return ret_frame


def get_tweets_for_user(username: str, filter_retweets=True) -> [str]:
    user = None
    tweets = []

    try:
        user = api.get_user(username, tweet_mode='extended')
    except tw.TweepError as error:
        print(f'Could not find user with username: {username} because {error.reason}')
        print(error.api_code)

    if user.protected is not True:
        if filter_retweets:
            for tweet in api.user_timeline(user.id):
                if str(tweet.text).startswith('RT') is False:
                    tweets.append(tweet)

            return tweets
        else:
            return api.user_timeline(user.id)
    else:
        return "PRIVATE"


# Assembles a pandas dataframe out of the frequency of specific words - Currently unused
def build_frequency_frame(data: []) -> pd.DataFrame:
    word_counter = {}
    word_list = []
    freq_list = []

    for word in data:

        if word in word_counter.keys():
            new_count = int(word_counter[word]) + 1
            word_counter[word] = new_count
        else:
            word_counter[word] = 1

    for word in word_counter.keys():
        word_list.append(word)
    for freq in word_counter.values():
        freq_list.append(freq)

    ret_frame = pd.DataFrame({"word": word_list, "freq": freq_list}).sort_values(by=["freq"], ascending=False)

    return ret_frame


# Removes 'RT' and '#' from tweets and selects for meaningful words
def strip_tweets(whole_tweet_list: str) -> [str]:
    stripped_tweet = []

    for whole_tweet in whole_tweet_list:
        for phrase in whole_tweet.split(" "):
            if phrase == "RT" or phrase.startswith("@") or phrase.isalnum() is not True:
                phrase = "pass"
            else:
                if phrase.lower() in stopwords.words('english'):
                    phrase = "pass"
            if phrase is not "pass":
                stripped_tweet.append(phrase)

    return stripped_tweet


def search_network(root_user: str, should_save=True) -> []:
    network_ids = []
    network_tweets = []

    try:
        user = api.get_user(root_user, tweet_mode='extended')
    except tw.TweepError as error:
        print(f'Could not find user with username: {root_user} because {error.reason}')
        print(error.api_code)

    network_ids.append(user.id)

    for follower_id in tw.Cursor(api.followers_ids, id=root_user).items(50):
        try:
            follower = api.get_user(follower_id)
        except tw.TweepError as error:
            print(f'An error occurred trying to find follower with ID: {follower_id} because {error.reason}')

        if follower.protected is not True:
            network_ids.append(follower_id)

    for id in network_ids:
        net_user_tl = api.user_timeline(id)

        for tweet in net_user_tl:
            if str(tweet.text).startswith('RT') is False:
                network_tweets.append(tweet.text)

    network_words = strip_tweets(network_tweets)
    network_frame = build_frequency_frame(network_words)

    if should_save:
        network_frame.to_csv(make_file_name_for_search(search=root_user, type='network'))

    return network_frame
