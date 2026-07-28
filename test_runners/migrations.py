from test_runners.simple_view import API_test_case


class ES_index_exists( API_test_case ):
    model = None

    @classmethod
    def setUpClass( cls ):
        super().setUpClass()
        if cls.model is None:
            raise NotImplementedError(
                f"se tiene que definir el atributo {cls.__class__}.model" )

    def test_index_exists( self ):
        index_exists = self.model._index.exists()
        self.assertTrue( index_exists )
