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
    Uses Welch's t-test on the indicated variables. Scipy by default does a one-sample test, so changes to the p-value
    are required
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
