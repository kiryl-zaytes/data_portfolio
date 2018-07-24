import matplotlib as mpl

from config import data
from data_preparation import Cleaner

mpl.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns


def plot_nans(before, after):
    fig, (ax1, ax2) = plt.subplots(ncols=2, sharey=True, figsize=(60, 15))
    x, y = zip(*before)
    x1, y1 = zip(*after)
    sns.barplot(x=list(x), y=list(y), ax=ax1)
    sns.barplot(x=list(x1), y=list(y1), ax=ax2)
    plt.setp(ax1.get_xticklabels(), rotation='vertical', fontsize=5)
    plt.setp(ax2.get_xticklabels(), rotation='vertical', fontsize=5)
    plt.show()


def plot_bar(points):
    fig, ax = plt.subplots(figsize=(20, 8))
    ax = sns.barplot(x=list(points[0]), y=list(points[1]))
    plt.setp(ax.get_xticklabels(), rotation='vertical', fontsize=10)
    plt.show()


if __name__ == '__main__':
    cleaner  = Cleaner(data_paths=data)
    before_cleaning = Cleaner.count_nan_columns(cleaner.azdias)
    cleaner.to_nan()
    after_cleaning = Cleaner.count_nan_columns(cleaner.azdias)
    plot_nans(before=before_cleaning, after=after_cleaning)
    sorted_yielder = Cleaner.sort_by_values(dict(after_cleaning))
    plot_bar(list(sorted_yielder))