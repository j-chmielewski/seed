import unittest

from seed import Seed


class TestSeed(unittest.TestCase):

    def setUp(self):
        self.seed = Seed(seed_list='./testing/seedlist')

    def test_print_help(self):
        self.assertIsNone(self.seed.print_help())

    def test_get_seeds(self):
        self.assertIsNotNone(self.seed.get_seeds())

    def test_print_seeds(self):
        self.assertIsNone(self.seed.print_seeds())

    def test_plant_seed(self):
        with self.assertRaises(SystemExit):
            self.seed.plant_seed()


if __name__ == '__main__':
    unittest.main(buffer=True)
