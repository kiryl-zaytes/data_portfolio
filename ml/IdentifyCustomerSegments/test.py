import unittest

from config import data
from data_preparation import Cleaner


class TestData(unittest.TestCase):
    def test_load_data(self):
        cleaner = Cleaner(data_paths=data)
        self.assertEqual(cleaner.azdias.shape, (891221, 85), "Shape of demography data")
        self.assertEqual(cleaner.customers.shape, (191652, 85), "Shape of customers data")
        self.assertEqual(cleaner.summary.shape, (85, 4), "Shape of customers data")


if __name__ == '__main__':
    unittest.main()