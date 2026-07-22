import unittest
from unittest.mock import Mock, patch
from chibi_django.elasticsearch.operations import Elasticsearch_index


class Test_Elasticsearch_index( unittest.TestCase ):

    def test_get_model_imports_correctly( self ):
        op = Elasticsearch_index( 'unittest.mock.Mock' )
        model = op._get_model()
        self.assertIs( model, Mock )

    def test_database_forwards_do_nothing_if_exists( self ):
        model = Mock()
        model._index.exists.return_value = True

        op = Elasticsearch_index( 'fake.path.Model' )
        with patch.object( op, '_get_model', return_value=model ):
            mock_function = (
                'chibi_django.elasticsearch.operations.'
                'create_index_if_not_exists'
            )
            with patch( mock_function ) as create_mock:
                op.database_forwards( 'app', None, None, None )

                model._index.delete.assert_not_called()
                create_mock.assert_called_once_with( model )

    def test_database_forwards_skips_delete_when_not_exists( self ):
        model = Mock()
        model._index.exists.return_value = False

        op = Elasticsearch_index( 'fake.path.Model' )
        with patch.object( op, '_get_model', return_value=model ):
            mock_function = (
                'chibi_django.elasticsearch.operations.'
                'create_index_if_not_exists'
            )
            with patch( mock_function ) as create_mock:
                op.database_forwards( 'app', None, None, None )

                model._index.delete.assert_not_called()
                create_mock.assert_called_once_with( model )

    def test_database_backwards_deletes_index( self ):
        model = Mock()
        model._index.exists.return_value = True

        op = Elasticsearch_index( 'fake.path.Model' )
        with patch.object( op, '_get_model', return_value=model ):
            op.database_backwards( 'app', None, None, None )
            model._index.delete.assert_called_once()

    def test_deconstruct_returns_serializable_args( self ):
        model_example = 'django_app.models.ES_model'
        op = Elasticsearch_index( model_example )
        name, args, kw = op.deconstruct()
        self.assertEqual( args, [ model_example ] )
        self.assertEqual( kw, {})

    def test_describe_mentions_model_path( self ):
        model_example = 'django_app.models.ES_model'
        op = Elasticsearch_index( model_example )
        self.assertIn( model_example, op.describe() )
