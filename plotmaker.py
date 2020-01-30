import os
import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress

import statsmanager as sm


class PlotMaker:
    """
    Generates visualizations of specified data. Requires a specified title and data.
    """

    def __init__(self, plot_title: str, plot_data: pd.DataFrame, plot_caption=''):
        self.title = plot_title
        self.caption = plot_caption
        self.data = plot_data

        styles = ['ggplot', 'fivethirtyeight', 'classic', 'bmh', 'seaborn-dark']
        style = random.choice(styles)

        assert isinstance(style, str)
        plt.style.use('ggplot')

    @staticmethod
    def make_file_name_for_plot(subject: str) -> str:
        """
        Generates a simple, plug and go file name for the plot
        :param subject: What the plot is about. Has _plot.png appended to the end when making the file name
        :return: A file path for the plot image as a string
        """
        file_name = os.getcwd() + '/' + subject + '/' + subject.lower().replace(' ', '_') + '_plot.png'
        path = os.getcwd() + '/' + subject + '/'

        if os.path.exists(path) is not True:
            try:
                os.mkdir(path)
            except IOError:
                print(f'Could not make path {path} !')

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

        if explan_var.empty is not True and response_var.empty is not True:
            if do_reg:
                lin_model = linregress(explan_var, response_var)
                slope = lin_model.slope
                intercept = lin_model.intercept

                r_val = round(lin_model.rvalue, 4)
                r_sq = round(r_val ** 2, 4)
                p_val = round(lin_model.pvalue, 4)
                std_err = round(lin_model.stderr, 4)

                actual_vals = response_var.tolist()
                explan_list = explan_var.tolist()

                resid_frame = sm.calculate_resids(slope, intercept, actual_vals, x_vals=explan_list)
                over_est = []
                under_est = []

                for value in resid_frame['resid']:
                    if value > 0:
                        over_est.append(value)
                    elif value < 0:
                        under_est.append(value)

                avg_over_est = round(np.mean(over_est), 4)
                avg_under_est = round(np.mean(under_est), 4)
                avg_resid = round(resid_frame['resid'].mean(), 4)

                fig_cap = f'r: {r_val} r^2: {r_sq} p-value: {p_val} std error: {std_err}\n ' \
                          f'Avg Overestimate: {avg_over_est} Avg Underestimate: {avg_under_est} ' \
                          f'Avg residual: {avg_resid}'

                plt.plot(explan_var, slope * explan_var + intercept, color='red')
                plt.figtext(0.05, 0.005, fig_cap, wrap=True, horizontalalignment='left', fontsize=10)
                # The plot needs to be made a bit taller to fit the caption
                plt.gcf().set_size_inches(11, 7)

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

    def build_boxplot(self, save_name: str, do_save=True, xlabels=[], stats=[]):
        """
        Generates a boxplot based on the provided data with optional defined x-axis labels.
        :param stats: Optional statistics to show as a caption
        :param xlabels: Optional labels for the x-axis
        :param save_name: The basic name of the plot to be saved
        :param do_save: Whether or not the plot is saved
        """

        green_diamond = dict(markerfacecolor='green', marker='D')

        plt.boxplot(self.data, flierprops=green_diamond)
        plt.title(self.title)
        plt.xlabel("Category")
        plt.ylabel("Count")

        if xlabels is not []:
            # Calling plt.xticks() with no args returns a tuple of the x-axis tick locations and there labels
            # Here we keep the locations the same, but replace the x labels with the specified ones using plt.xticks().
            locations, labels = plt.xticks()
            plt.xticks(locations, xlabels)
            # Ensures that all the words on the boxplot's x-axis render properly
            plt.gcf().set_size_inches(11, 5)

        if do_save:
            file_name = self.make_file_name_for_plot(save_name)
            try:
                plt.savefig(file_name, dpi=150)
            except FileNotFoundError as error:
                print(f'Could not find {error.filename}! Check directory name?')

        plt.show()
