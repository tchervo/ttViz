import pandas as pd
from nltk.corpus import stopwords
import TweetPlot

tw = TweetPlot.tw
api = TweetPlot.api


# Saves tweets to a CSV file named after their topic
def save_tweets(topic: str):
    tweet_text = []
    tweet_ids = []
    tweet_favorites = []
    tweet_retweets = []
    tweets = tw.Cursor(api.search, q=topic).items(50)

    for tweet in tweets:
        tweet_text.append(tweet.text)
        tweet_ids.append(tweet.id)
        tweet_favorites.append(int(tweet.favorite_count))
        tweet_retweets.append(int(tweet.retweet_count))

    tweet_frame = pd.DataFrame(data={"Tweet ID": tweet_ids, "Text": tweet_text, "Favorites": tweet_favorites,
                                     "Retweets": tweet_retweets})
    tweet_frame.to_csv(topic + ".csv")

    test = pd.read_csv(topic + ".csv")

    print(test.head())


# Loads tweets from CSV and returns an array of the tweets' text
def load_tweets(topic: str) -> [str]:
    tweet_text = []
    file_name = topic + ".csv"
    tweet_frame = pd.read_csv(file_name)

    print(tweet_frame.head())

    for text in tweet_frame.Text:
        tweet_text.append(text)

    return tweet_text


# Assembles a pandas dataframe out of the frequency of specific words
def build_dataframe(data: []) -> pd.DataFrame:
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

    ret_frame = pd.DataFrame({"Word": word_list, "Freq": freq_list}).sort_values(by=["Freq"], ascending=False)

    return ret_frame


# Removes 'RT' and '#' from tweets and selects for meaningful words
def strip_tweet(whole_tweet_list: str) -> [str]:
    stripped_tweet = []
    punc = ['.', ',', ';', '?', '!']

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
