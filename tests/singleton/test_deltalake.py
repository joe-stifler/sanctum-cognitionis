from singleton.deltalake import Deltalake

class TestDeltalake(unittest.TestCase):
    def test_singleton_behavior(self):
        lake1 = Deltalake()
        lake2 = Deltalake()
        self.assertEqual(id(lake1), id(lake2))

    def test_data_integration(self):
        lake = Deltalake()
        data = lake.read_data({'query': 'select * from data'})
        self.assertIsInstance(data, pd.DataFrame)  # Assume que você implementou essa função

if __name__ == '__main__':
    unittest.main()
