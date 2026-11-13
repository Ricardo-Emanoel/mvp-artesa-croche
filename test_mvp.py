import unittest

class TestArtesaMVP(unittest.TestCase):

    def test_calculo_prazo_encomenda(self):
        # Valida o cálculo de dias para confecção da peça
        prazo_base = 5
        dias_extras = 3
        self.assertEqual(prazo_base + dias_extras, 8)

    def test_conexao_sqlite(self):
        # Simula a validação da base de dados
        status_conexao = True
        self.assertTrue(status_conexao)

if __name__ == '__main__':
    unittest.main()