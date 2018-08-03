from operator import itemgetter
import pandas as pd
import numpy as np
import sys

from config import features_codes_toremap


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

    @staticmethod
    def to_nan(df, mapping):
        for index, r in mapping.iterrows():
            m_u = r.missing_or_unknown[1:-1].split(',')
            ind = df[r.attribute].isin(m_u)
            df.loc[ind, r.attribute] = np.NaN
        return df

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
        decade_mapping = features_codes_toremap['mapping_decade']
        movement_mapping = features_codes_toremap['mapping_movement']

        def convert_mapping(s):
            if np.isnan(s):
                new_dec.append(np.nan)
                new_mov.append(np.nan)
            else:
                new_dec.append(decade_mapping[np.int(s)])
                new_mov.append(movement_mapping[np.int(s)])

        return convert_mapping

    @staticmethod
    def remap_lebensphase(df):

        ftr = df['LP_LEBENSPHASE_FEIN']  # add to drop list and GB

        def age():
            new_f = np.full(df.shape[0], -1)
            for g, t in enumerate(features_codes_toremap['mapping_age']):
                ind = ((ftr.values >= t[0]) & (ftr.values < t[1]))
                new_f[ind] = g
            df['age'] = new_f

        def income(mapp, name):
            new_f = np.full(df.shape[0], -1)
            for k, v in mapp.items():
                new_f[ftr.isin(v)] = k
            df[name] = new_f

        age()
        income(features_codes_toremap['mapping_income'], 'income')
        income(features_codes_toremap['mapping_group'], 'group')


    @staticmethod
    def print_values(df, list_feature):
        for x in list_feature:
            print('{}\n {}'.format(x, df[x].value_counts()))
