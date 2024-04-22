from dal.data_abstraction_layer import DataAbstractionLayer

class TestDataAbstractionLayer(unittest.TestCase):
    def setUp(self):
        self.dal = DataAbstractionLayer({'csv': CSVConnector('/path/to/csv'), 'deltalake': Deltalake()})

    def test_data_retrieval_from_csv(self):
        data = self.dal.get_data({'source': 'csv'})
        self.assertIsInstance(data, pd.DataFrame)

    def test_data_retrieval_from_deltalake(self):
        data = self.dal.get_data({'source': 'deltalake'})
        self.assertIsInstance(data, pd.DataFrame)

if __name__ == '__main__':
    unittest.main()
