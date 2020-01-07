import os

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import linregress


class PlotMaker:
    """
    Generates visualizations of specified data. Requires a specified title
    """

    def __init__(self, plot_title: str, plot_data: pd.DataFrame, plot_caption=''):
        self.title = plot_title
        self.caption = plot_caption
        self.data = plot_data

    def make_file_name_for_plot(self, subject: str) -> str:
        """
        Generates a simple, plug and go file name for the plot
        :param subject: What the plot is about. Has _plot.png appended to the end when making the file name
        :return: A file path for the plot image as a string
        """
        file_name = os.getcwd() + '/' + subject + '/' + subject.lower().replace(' ', '_') + '_plot.png'

        return file_name

    def build_scatter_plot(self, explanatory: str, response: str, subject: str, do_reg=True, do_save=True):
        """
        Creates a scatter plot using the user specified data and explanatory/response variables
        Explanatory and response variables should be column names in the dataframe. do_reg determines if linear
        regression should be ran
        :param explanatory: The name of the explanatory variable (x variable) for the plot
        :param response: The name of the response variable (y variable) for the plot
        :param subject: The subject of the plot. Is used to create the plot's save name
        :param do_reg: Whether or not to perform linear regression. Defautl is True.
        :param do_save: Whether or not to save an image of the plot. Default is True.
        """

        print(self.title)
        explan_var = self.data[explanatory]
        response_var = self.data[response]

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

    def build_bar_plot(self, x_var: str, y_var: str, subject: str, do_save=True):
        """
        Creates a bar plot using the user specified data, the name of the variable to be plotted
        along the x-axis (x_var), and the heights of the bars (y_var).
        :param x_var: The name of the variable to plot on the x-axis. Can be continious, discrete, or categorical
        :param y_var: The heights of the bars to plot
        :param subject: The subject of the bar graph. Used to create image name.
        :param do_save: Whether or not to save an image of the plot. Default is True
        """

        print(self.title)
        if len(self.data[x_var]) > 10:
            # Selects the first 10 rows (first list), then the first two columns(second list)
            valid_data = self.data.iloc[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1]]
        else:
            valid_data = self.data

        x_vals = valid_data[x_var]
        heights = valid_data[y_var]

        if x_vals.empty is True or heights.empty is True:
            print("No tweets about this topic or not enough data!")
        else:
            plt.bar(x=x_vals, height=heights)
            plt.title(self.title)
            plt.xlabel(x_var.capitalize())
            plt.ylabel(y_var.capitalize())

            # Ensures that all the words on the bar graph render properly
            plt.gcf().set_size_inches(11, 5)

            if do_save:
                file_name = self.make_file_name_for_plot(subject)
                try:
                    plt.savefig(file_name, dpi=150)
                except FileNotFoundError as error:
                    print(f'Could not find {error.filename}! Check directory name?')

            plt.show()
