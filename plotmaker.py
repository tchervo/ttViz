import os

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import linregress


class PlotMaker:

    title = ''
    caption = ''

    def __init__(self, plot_title: str, plot_caption=''):
        self.title = plot_title
        self.caption = plot_caption

    # Generates a simple, plug and go file name for the plot
    def make_file_name_for_plot(self, subject: str) -> str:
        file_name = os.getcwd() + '/' + subject + '/' + subject.lower().replace(' ', '_') + '_plot.png'

        return file_name

    # Creates a scatter plot using the user specified data and explanatory/response variables
    # Explanatory and response variables should be column names in the dataframe. do_reg determines if linear
    # regression should be ran
    def build_scatter_plot(self, data: pd.DataFrame, explanatory: str, response: str, subject: str, do_reg=True,
                           do_save=True):
        print(self.title)
        explan_var = data[explanatory]
        response_var = data[response]

        plt.scatter(explan_var, response_var)

        plt.title(self.title)
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
            if do_save:
                file_name = self.make_file_name_for_plot(subject)
                try:
                    plt.savefig(file_name, dpi=150)
                except FileNotFoundError as error:
                    print(f'Could not find {error.filename}! Check directory name?')

            plt.show()
        else:
            print("No tweets about this topic!")

    # Creates a bar plot using the user specified data and x_var, the name of the variable to be plotted
    # along the x-axis. Currently broken
    def build_bar_plot(self, data: pd.DataFrame, x_var: str, y_var: str, subject: str, do_save=True):
        print(self.title)
        if len(data[x_var]) > 10:
            # Selects the first 10 rows (first list), then the first two columns(second list)
            valid_data = data.iloc[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1]]
        else:
            valid_data = data

        x_vals = valid_data[x_var]
        heights = valid_data[y_var]
        if x_vals.empty is True or heights.empty is True:
            print("No tweets about this topic or not enough data!")
        else:
            plt.bar(x=x_vals, height=heights)
            plt.title(self.title)
            plt.xlabel(x_var.capitalize())
            plt.ylabel(y_var.capitalize())

            if do_save:
                file_name = self.make_file_name_for_plot(subject)
                try:
                    plt.savefig(file_name, dpi=150)
                except FileNotFoundError as error:
                    print(f'Could not find {error.filename}! Check directory name?')

            plt.show()
