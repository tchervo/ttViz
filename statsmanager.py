import scipy.stats as stats

import tweetplot

api = tweetplot.api
tw = tweetplot.tw


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
