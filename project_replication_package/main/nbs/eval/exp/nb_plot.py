
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: dev_nb/plot_figures.ipynb

from typing import List
import matplotlib.pyplot as plt
import numpy as np
def box_whisker_plot(numbers: List,
                     title: str,
                     xlabel: str,
                     ylabel: str):
    fig = plt.figure(1, figsize=(9,6))
    ax1 = fig.add_subplot(2,1,1)
    ax1.set_title(title)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax1.boxplot(numbers, 0, 'rs', 0)
    return fig
