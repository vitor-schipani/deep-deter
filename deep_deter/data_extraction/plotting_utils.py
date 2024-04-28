# Data Science
import pandas as pd
import matplotlib.pyplot as plt


def plot_category_counts_horizontal(df, column_name):
    """
    Plots a horizontal bar chart of the counts of each category in a given column of a DataFrame.

    Parameters:
    - df: pandas.DataFrame containing the data
    - column_name: string, the name of the column to plot the counts for

    Returns:
    - A matplotlib horizontal bar chart showing the counts of each category in the specified column.
    """
    # Calculate the counts of each category
    counts = df[column_name].value_counts()

    # Plot the counts
    plt.figure(figsize=(10, 6))
    counts.plot(kind='barh')  # Change here for horizontal bar chart
    plt.title(f'Counts of Each Category in {column_name}')
    plt.xlabel('Counts')
    plt.ylabel('Category')
    plt.show()
