class TestLLMBaseFactory(unittest.TestCase):

    def setUp(self):
        self.llm_client = Mock()

    def test_create_base_llm_default(self):
        llm = LLMBaseFactory.create_base_llm(llm_client=self.llm_client)
        self.assertIsInstance(llm, LLMBase)

    def test_create_base_llm_redacao(self):
        llm = LLMBaseFactory.create_base_llm('redacao', self.llm_client)
        self.assertIsInstance(llm, LLMRedacao)
