import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import linregress


# Creates a scatter plot using the user specified data and explanatory/response variables
# Explanatory and response variables should be column names in the dataframe. do_reg determines if linear
# regression should be ran
def build_scatter_plot(data: pd.DataFrame, explanatory: str, response: str, subject: str, do_reg=True):
    explan_var = data[explanatory]
    response_var = data[response]

    plt.scatter(explan_var, response_var)

    plt.title(f'{response.capitalize()} as a function of {explanatory.capitalize()} for {subject}')
    plt.xlabel(explanatory.capitalize())
    plt.ylabel(response.capitalize())

    if do_reg:
        lin_model = linregress(explan_var, response_var)
        slope = lin_model.slope
        intercept = lin_model.intercept

        r_val = round(lin_model.rvalue, 4)
        r_sq = round(r_val ** 2, 4)
        p_val = round(lin_model.pvalue, 4)
        fig_cap = f'r: {r_val} r^2: {r_sq} p-value: {p_val}'

        plt.plot(explan_var, slope * explan_var + intercept, color='red')
        plt.figtext(0.05, 0.0005, fig_cap, wrap=True, horizontalalignment='left', fontsize=10)

    subject_file = '/' + subject.replace('@', '') + '/' + subject.replace('@', '') + '.png'

    if explan_var.empty is not True and response_var.empty is not True:
        plt.savefig('subject_file.png', dpi=150)
        plt.show()
    else:
        print("No tweets about this topic!")


# Creates a bar plot using the user specified data and x_var, the name of the variable to be plotted
# along the x-axis. Currently broken
def build_bar_plot(data: pd.DataFrame, x_var: str, y_var: str, subject: str):
    x_vals = data[x_var]
    heights = data[y_var]

    if x_vals.empty is True or heights.empty is True:
        print("No tweets about this topic!")
    else:
        plt.bar(x=x_vals, height=heights)
        plt.title(f'{y_var.capitalize()} of {x_var.capitalize()} Used When Tweeting About {subject.capitalize()}')
        plt.xlabel(x_var.capitalize())
        plt.ylabel(y_var.capitalize())
        plt.show()


