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
            ind = self.azdias[r.attribute].isin(m_u)
            self.azdias.loc[ind, r.attribute] = np.NaN

    def nan_to_category(self, category_name):
        attr = self.summary[self.summary.type == 'categorical']['attribute']
        try:
            for a in attr:
                res = self.azdias[a].isnull()
                self.azdias.loc[res.index, a] = category_name
        except KeyError:
            print('Key is not in list' + a)

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
        return azdias_less, azdias_gr, less_trh, gr_trh

    @staticmethod
    def remap_jugendjahre(new_dec=None, new_mov=None):

        decade_mapping = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 3, 8: 4, 9: 4, 10: 5, 11: 5, 12: 5, 13: 5, 14: 6,
                          15: 6}
        movement_mapping = {1: 0, 2: 1, 3: 0, 4: 1, 5: 0, 6: 1, 7: 1, 8: 0, 9: 1, 10: 0, 11: 1, 12: 0, 13: 1, 14: 0,
                            15: 1}

        def convert_mapping(s):
            if np.isnan(s):
                new_dec.append(np.nan)
                new_mov.append(np.nan)
            else:
                new_dec.append(decade_mapping[np.int(s)])
                new_mov.append(movement_mapping[np.int(s)])

        return convert_mapping

    def remap_lebensphase(self):
        mapping = [(1,14), (14,21), (21,24), (24,29), (29,41)]
        ftr = self.azdias['LP_LEBENSPHASE_FEIN']
        new_f = np.full(self.azdias.shape[0], -1)

        def change(i, j, level=0):
            ind = (ftr.values >= i) & (ftr.values < j)
            new_f[ind] = level

        for g, t in enumerate(mapping):
            change(*t, level=g)
            
        self.azdias['age'] = new_f


    @staticmethod
    def print_values(df, list_feature):
        for x in list_feature:
            print('{}\n {}'.format(x, df[x].value_counts()))
