import pandas as pd
import scipy.stats as stats


def is_normal_dist(data):
    """
    Uses scipy's normality test to determine whether a distribution of data is normal. Only valid when n > 20
    :param data: The data to be analyzed
    :return: True if the p value for the test is less than 0.05, False otherwise
    """

    if len(data) < 20:
        print('Kurtosis test is not valid for n < 20, so normal test cannot be run!')

        return None
    else:
        statistic, p_val = stats.normaltest(data, nan_policy='omit')

        print(f'Statistic for normal test (k^2 + s^2): {statistic}')

        if p_val < 0.05:
            print(p_val)
            return True
        else:
            return False


def do_t_test(data1: pd.DataFrame, data2: pd.DataFrame, mode='interactions') -> tuple:
    """
    Uses Welch's t-test on the indicated variables. Scipy by default does a two-sided test, so changes to the p-value
    are required if a one-sided test is requested.
    :param data1: A pandas dataframe
    :param data2: A pandas dataframe
    :param mode: What sort of data should the t-test analyze. Default is interactions
    :return: A tuple of the p value and test statistic. Number of each may vary by mode.
    """

    if mode == 'interactions':
        # For favorites
        fav_stat, fav_p_val = stats.ttest_ind(data1['favorites'], data2['favorites'], equal_var=False,
                                              nan_policy='omit')

        # For retweets
        rt_stat, rt_p_val = stats.ttest_ind(data1['retweets'], data2['retweets'], equal_var=False,
                                            nan_policy='omit')

        return fav_stat, fav_p_val, rt_stat, rt_p_val


def format_tweet_from_stats(data: tuple, test_type='t', opt_data=[]) -> str:
    """
    Creates a tweet with statistical information in it.
    :param opt_data: Optional data to be formatted into the tweet.
    :param data: The statistics to be formatted into the tweet.
    :param test_type: The type of statistical test being performed. Defaults to a t-test
    :return: A string that can be posted as a tweet
    """

    if test_type == 't':
        fav_stat, fav_p_val, rt_stat, rt_p_val = data
        user1 = opt_data[0]
        user2 = opt_data[1]
        sig_fav = fav_p_val < 0.05
        sig_rt = rt_p_val < 0.05

        if sig_fav and not sig_rt:
            if fav_stat > 0:
                return f'@{user1} has statistically more favorites on their tweets than @{user2}! ' \
                       f'(p-value: {fav_p_val} t-statistic: {fav_stat}'
            else:
                return f'@{user2} has statistically more favorites on their tweets than @{user1}! ' \
                       f'(p-value: {fav_p_val} t-statistic: {fav_stat * -1}'
        if sig_rt and not sig_fav:
            if rt_stat > 0:
                return f'@{user1} has statistically more retweets on their tweets than @{user2}! p-value: {rt_p_val}' \
                       f' t-statistic: {rt_stat}'
            else:
                return f'@{user2} has statistically more retweets on their tweets than @{user1}! p-value: {rt_p_val}' \
                       f' t-statistic: {rt_stat * -1}'
        if sig_rt and sig_fav:
            if rt_stat > 0 and fav_stat > 0:
                return f'@{user1} has statistically more favorites and retweets on their tweets than @{user2}! ' \
                       f'(p-value: {fav_p_val} (Favorites), {rt_p_val} (Retweets) t-statistic: {fav_stat} (Favorites)' \
                       f', {rt_stat} (Retweets)'
            else:
                return f'@{user2} has statistically more favorites and retweets on their tweets than @{user1}! ' \
                       f'(p-value: {fav_p_val} (Favorites), {rt_p_val} (Retweets) t-statistic: {fav_stat * -1}' \
                       f'(Favorites), {rt_stat * -1} (Retweets)'
        if not sig_rt and not sig_fav:
            return f' Neither @{user1} or @{user2} have statistically more retweets or favorite than the other!' \
                   f'(p-value: {fav_p_val} (Favorites), {rt_p_val} (Retweets) t-statistic: {fav_stat} (Favorites)' \
                   f', {rt_stat} (Retweets)'




