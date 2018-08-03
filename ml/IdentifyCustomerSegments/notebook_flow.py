from config import data
from data_preparation import Cleaner
import pandas as pd
import numpy as np

from visuals import plot_bars
from sklearn.preprocessing import Imputer

if __name__ == '__main__':
    cleaner = Cleaner(data_paths=data)


    def split_by_missingvalues():
        before_cleaning = Cleaner.count_nan_columns(cleaner.azdias)
        cleaner.to_nan()
        after_cleaning = Cleaner.count_nan_columns(cleaner.azdias)
        l, g, s1,s2 = Cleaner.split_by_treshhold(cleaner.azdias)
        cleaner.azdias = l
        return before_cleaning, after_cleaning, l.shape, g.shape


    def recode(df):
        df = Cleaner.recode(df, 'ANREDE_KZ', 2, 0)
        df = Cleaner.recode(df, 'OST_WEST_KZ', 'O', 0)
        df = Cleaner.recode(df, 'OST_WEST_KZ', 'W', 1)
        return df


    def extract_features(df):
        new_dec = []
        new_mov = []
        to_apply = Cleaner.remap_jugendjahre(new_dec=new_dec, new_mov=new_mov)
        df['PRAEGENDE_JUGENDJAHRE'].apply(to_apply)
        df['decade'] = np.array(new_dec)
        df['movement'] = np.array(new_mov)
        df['wealth'] = df['CAMEO_INTL_2015'].str[0]
        df['life_stage'] = df['CAMEO_INTL_2015'].str[1]
      #  cleaner.azdias = cleaner.azdias.drop(['CAMEO_INTL_2015', 'PRAEGENDE_JUGENDJAHRE', 'LP_LEBENSPHASE_GROB'],
                                            # axis=1)
        new_mov, new_dec = None, None
        return df

    def drop(df):
        return df.drop(['AGER_TYP',
                                              'TITEL_KZ',
                                              'KK_KUNDENTYP',
                                              'KBA05_BAUMAX',
                                              'LP_FAMILIE_FEIN',
                                              'LP_STATUS_FEIN',
                                              'NATIONALITAET_KZ',
                                              'CAMEO_DEU_2015',
                                              'CAMEO_INTL_2015',
                                              'PRAEGENDE_JUGENDJAHRE',
                                              'LP_LEBENSPHASE_GROB'],
                                             axis=1)

    def dummies(df):
        cols = ['LP_FAMILIE_GROB',
                'LP_STATUS_GROB',
                'SHOPPER_TYP',
                'SOHO_KZ',
                'VERS_TYP',
                'ZABEOTYP',
                'GEBAEUDETYP',
                'OST_WEST_KZ',
                'CAMEO_DEUG_2015',
                'PLZ8_BAUMAX',
                'WOHNLAGE',
                'LP_LEBENSPHASE_FEIN',
                'decade',
                'wealth',
                'life_stage',
                'ALTER_HH'
                ]
        df = pd.get_dummies(df, columns=cols)
        return df


def clean_data(df):
    l, g, less_trh, gr_trh = Cleaner.split_by_treshhold(df, treshold=34)
    df = l
    df = Cleaner.to_nan(df, cleaner.summary)
    df = recode(df)
    df = extract_features(df)
    df = drop(df)
    df = dummies(df)
    return df



clean_data(cleaner.customers)


split_by_missingvalues()
recode()
extract_features()
cleaner.remap_lebensphase()
#drop()

#dummies()
nc = Cleaner.count_nan_columns(cleaner.azdias)
nw = Cleaner.count_nan_rows(cleaner.azdias)

#plot_bars(dict(nc))

Cleaner.print_values(cleaner.azdias, ['PLZ8_ANTG1','PLZ8_ANTG2', 'PLZ8_ANTG3','PLZ8_ANTG4','PLZ8_BAUMAX','PLZ8_HHZ','PLZ8_GBZ'])
nc1 = Cleaner.count_nan_columns(cleaner.azdias[['PLZ8_ANTG1','PLZ8_ANTG2', 'PLZ8_ANTG3','PLZ8_ANTG4','PLZ8_BAUMAX','PLZ8_HHZ','PLZ8_GBZ']])



cleaner.nan_to_category(category_name=-1)


imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
x = imp.fit_transform(cleaner.azdias)

print(nc1)
#print(nw.value_counts())

cleaner.summary[cleaner.summary.type == 'categorical']