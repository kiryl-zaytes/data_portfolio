from operator import itemgetter
import pandas as pd
import numpy as np
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

    @staticmethod
    def filterout_zeros(dic):
        return {k: v for k, v in dic.items() if v != 0}

    @staticmethod
    def sort_by_values(dic):
        filtered = Cleaner.filterout_zeros(dic)
        sor = zip(*sorted(filtered.items(), key=itemgetter(1)))
        return sor

