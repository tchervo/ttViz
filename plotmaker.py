import matplotlib.pyplot as plt
import pandas as pd


# Creates a plot using the user specified data and explanatory/response variables
# Explanatory and response variables should be column names in the dataframe
def build_plot(data: pd.DataFrame, explanatory: str, response: str, subject: str):
    explan_var = data[explanatory]
    response_var = data[response]

    plt.scatter(explan_var, response_var)

    plt.title(f'{response.capitalize()} as a function of {explanatory.capitalize()} for {subject}')
    plt.xlabel(explanatory.capitalize())
    plt.ylabel(response.capitalize())
    plt.show()

