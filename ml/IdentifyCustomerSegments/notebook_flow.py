from config import data
from data_preparation import Cleaner
import pandas as pd
import numpy as np

if __name__ == '__main__':
    cleaner = Cleaner(data_paths=data)


    def split_by_missingvalues():
        before_cleaning = Cleaner.count_nan_columns(cleaner.azdias)
        cleaner.to_nan()
        after_cleaning = Cleaner.count_nan_columns(cleaner.azdias)
        l, g = Cleaner.split_by_treshhold(cleaner.azdias)
        cleaner.azdias = l
        return before_cleaning, after_cleaning, l.shape, g.shape


    def recode():
        Cleaner.recode(cleaner.azdias, 'ANREDE_KZ', 2, 0)
        Cleaner.recode(cleaner.azdias, 'OST_WEST_KZ', 'O', 0)
        Cleaner.recode(cleaner.azdias, 'OST_WEST_KZ', 'W', 1)


    def extract_fetures():
        new_dec = []
        new_mov = []
        to_apply = Cleaner.remap_jugendjahre(new_dec=new_dec, new_mov=new_mov)
        cleaner.azdias['PRAEGENDE_JUGENDJAHRE'].apply(to_apply)
        cleaner.azdias['decade'] = np.array(new_dec)
        cleaner.azdias['movement'] = np.array(new_mov)
        cleaner.azdias['wealth'] = cleaner.azdias['CAMEO_INTL_2015'].str[0]
        cleaner.azdias['life_stage'] = cleaner.azdias['CAMEO_INTL_2015'].str[1]
        cleaner.azdias = cleaner.azdias.drop(['CAMEO_INTL_2015', 'PRAEGENDE_JUGENDJAHRE', 'LP_LEBENSPHASE_GROB'],
                                             axis=1)
        new_mov, new_dec = None, None


    def dummies():
        cols = ['LP_FAMILIE_GROB',
                'LP_STATUS_GROB',
                'SHOPPER_TYP',
                'SOHO_KZ',
                'VERS_TYP',
                'ZABEOTYP',
                'KK_KUNDENTYP',
                'GEBAEUDETYP',
                'OST_WEST_KZ',
                'CAMEO_DEUG_2015',
                'KBA05_BAUMAX',
                'PLZ8_BAUMAX',
                'WOHNLAGE',
                'LP_LEBENSPHASE_FEIN'
                ]
        cleaner.azdias = pd.get_dummies(cleaner.azdias, columns=cols)

split_by_missingvalues()
recode()
extract_fetures()
dummies()