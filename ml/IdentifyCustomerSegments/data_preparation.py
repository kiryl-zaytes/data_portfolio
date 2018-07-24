from operator import itemgetter
import pandas as pd
import numpy as np
import sys


class Cleaner:
    def __init__(self, data_paths, sep=';'):
        vals = data_paths.values()
        try:
            self._azdias, self.customers, self.summary = [pd.read_csv(v, sep=sep) for v in vals]
        except FileNotFoundError:
            sys.exit()

    @property
    def azdias(self):
        return self._azdias

    @azdias.setter
    def azdias(self, df):
        self._azdias = df

    @staticmethod
    def recode(df, feature, from_value, to_value):
        try:
            df.loc[df[feature] == from_value, feature] = to_value
        except KeyError:
            print('Provided keys not found, returning back initial set')
            return df
        return df

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
            ind = self._azdias[r.attribute].isin(m_u)
            self._azdias.loc[ind, r.attribute] = np.NaN

    @staticmethod
    def filterout_zeros(dic):
        return {k: v for k, v in dic.items() if v != 0}

    @staticmethod
    def sort_by_values(dic):
        filtered = Cleaner.filterout_zeros(dic)
        sor = zip(*sorted(filtered.items(), key=itemgetter(1)))
        return sor

    @staticmethod
    def split_by_treshhold(df, treshold=34):
        missing_rows = Cleaner.count_nan_rows(df)
        missing_rows = pd.DataFrame(missing_rows, columns=['amount'])
        less_trh = missing_rows[missing_rows.amount < treshold]
        gr_trh = missing_rows[missing_rows.amount >= treshold]
        azdias_less = df.iloc[less_trh.index]
        azdias_gr = df.iloc[gr_trh.index]
        return azdias_less, azdias_gr