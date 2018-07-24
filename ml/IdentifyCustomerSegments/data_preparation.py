from operator import itemgetter

from config import data
import pandas as pd
import matplotlib as mpl

mpl.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys


class Cleaner:
    def __init__(self, data_paths, sep=';'):
        vals = data_paths.values()
        try:
            self.azdias, self.customers, self.summary = [pd.read_csv(v, sep=sep) for v in vals]
        except FileNotFoundError:
            sys.exit()

    @staticmethod
    def count_nan_columns(df):
        res = []
        for c in df.columns:
            res.append(df[c].isnull().sum())
        return list(zip(df.columns, res))

    @staticmethod
    def count_nan_rows(df):
        return np.array(df.isnull().sum(axis=1).tolist())

    def to_nan(self):
        for index, r in self.summary.iterrows():
            m_u = r.missing_or_unknown[1:-1].split(',')
            ind = self.azdias[r.attribute].isin(m_u)
            self.azdias.loc[ind, r.attribute] = np.NaN


# def load_data(dict_path, sep=';'):
#     vals = dict_path.values()
#     files = [pd.read_csv(v, sep=sep) for v in vals]
#     return files


# def to_nan(df, features_summary):
#     for index, r in features_summary.iterrows():
#         m_u = r.missing_or_unknown[1:-1].split(',')
#         ind = df[r.attribute].isin(m_u)
#         df.loc[ind, r.attribute] = np.NaN


# def count_nan_columns(df):
#     res = []
#     for c in df.columns:
#         res.append(df[c].isnull().sum())
#     return list(zip(df.columns, res))
#
#
# def count_nan_rows(df):
#     return df.isnull().sum(axis=1).tolist()


def plot_nans(before, after):
    fig, (ax1, ax2) = plt.subplots(ncols=2, sharey=True)
    fig.set_size_inches(40, 20.5)
    x, y = zip(*before)
    x1, y1 = zip(*after)
    sns.barplot(x=list(x), y=list(y), ax=ax1)
    sns.barplot(x=list(x1), y=list(y1), ax=ax2)
    plt.setp(ax1.get_xticklabels(), rotation='vertical', fontsize=10)
    plt.setp(ax2.get_xticklabels(), rotation='vertical', fontsize=10)
    plt.show()


def plot_bar(points):
    fig, ax = plt.subplots(figsize=(20, 8))
    ax = sns.barplot(x=list(points[0]), y=list(points[1]))
    plt.setp(ax.get_xticklabels(), rotation='vertical', fontsize=10)
    plt.show()


def filterout_zeros(dic):
    return {k: v for k, v in dic.items() if v != 0}


def sort_by_values(dic):
    filtered = filterout_zeros(dic)
    sor = zip(*sorted(filtered.items(), key=itemgetter(1)))
    return sor


#azdias, customers, summary = load_data(data)
#before_cleaning = count_nan_columns(azdias)
#to_nan(azdias, summary)
#after_cleaning = count_nan_columns(azdias)
#plot_nans(before_cleaning, after_cleaning)


#sorted_yielder = sort_by_values(dict(after_cleaning))


#plot_bar(list(sorted_yielder))
#count_nan_rows(azdias)