import unittest

from config import data
from data_preparation import Cleaner


class TestData(unittest.TestCase):
    def __init__(self, *args):
        super().__init__(*args)
        self.cleaner = Cleaner(data_paths=data)

    def test_load_data(self):
        self.assertEqual(self.cleaner._azdias.shape, (891221, 85), "Shape of demography data")
        self.assertEqual(self.cleaner.customers.shape, (191652, 85), "Shape of customers data")
        self.assertEqual(self.cleaner.summary.shape, (85, 4), "Shape of customers data")

    def test_nans(self):
        nans_col = Cleaner.count_nan_columns(self.cleaner._azdias)
        nans_row = Cleaner.count_nan_rows(self.cleaner._azdias)
        d = dict(nans_col)
        self.assertEqual(d['CAMEO_DEUG_2015'], 98979)
        self.assertEqual(d['PLZ8_ANTG1'], 116515)
        self.assertEqual(nans_row.min(), 0)
        self.assertEqual(nans_row.max(), 46)

    def test_tonan(self):
        before_cleaning = Cleaner.count_nan_columns(self.cleaner._azdias)
        self.cleaner.to_nan()
        after_cleaning = Cleaner.count_nan_columns(self.cleaner._azdias)
        db =  dict(before_cleaning)
        da = dict(after_cleaning)
        self.assertEqual(db['AGER_TYP'], 0)
        self.assertEqual(da['AGER_TYP'], 685843)

    def test_split(self):
        l, g = Cleaner.split_by_treshhold(self.cleaner._azdias)
        self.assertEqual(l.shape, (798293, 85))
        self.assertEqual(g.shape, (92928, 85))

    def test_recode(self):
        Cleaner.recode(self.cleaner.azdias, 'ANREDE_KZ', 2, 0)
        Cleaner.recode(self.cleaner.azdias, 'OST_WEST_KZ', 'O', 0)
        Cleaner.recode(self.cleaner.azdias, 'OST_WEST_KZ', 'W', 1)

        t1 = self.cleaner.azdias[self.cleaner.azdias['ANREDE_KZ'] == 2]
        t2 = self.cleaner.azdias[self.cleaner.azdias['OST_WEST_KZ'] == 'O']
        t3 = self.cleaner.azdias[self.cleaner.azdias['OST_WEST_KZ'] == 'W']
        t4 = self.cleaner.azdias[self.cleaner.azdias['OST_WEST_KZ'] == 1]
        t5 = self.cleaner.azdias[self.cleaner.azdias['OST_WEST_KZ'] == 0]
        self.assertEqual(len(t1), 0)
        self.assertEqual(len(t2), 0)
        self.assertEqual(len(t3), 0)
        self.assertEqual(len(t4), 629528)
        self.assertEqual(len(t5), 168545)

if __name__ == '__main__':
    unittest.main()