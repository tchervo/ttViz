import pandas as pd
import scipy.stats as stats


def is_normal_dist(data):
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


# Uses Welch's t-test on the indicated variables. Scipy by default does a one-sample test,
# so changes to the p-value are required
def do_t_test(data1: pd.DataFrame, data2: pd.DataFrame, mode='interactions') -> tuple:
    if mode == 'interactions':
        # For favorites
        fav_stat, fav_p_val = stats.ttest_ind(data1['favorites'], data2['favorites'], equal_var=False,
                                              nan_policy='omit')

        # For retweets
        rt_stat, rt_p_val = stats.ttest_ind(data1['retweets'], data2['retweets'], equal_var=False,
                                            nan_policy='omit')

        ret_dat = (fav_stat, fav_p_val, rt_stat, rt_p_val)

        return ret_dat
