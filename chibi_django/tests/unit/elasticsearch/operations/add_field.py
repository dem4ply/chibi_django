from unittest import TestCase
from unittest.mock import Mock, patch

from elasticsearch.exceptions import NotFoundError

from chibi_django.elasticsearch.operations import Elasticsearch_add_field
from chibi_django.elasticsearch.exceptions import Elasticsearch_index_not_found


class Test_elasticsearch_add_field( TestCase ):
    def setUp( self ):
        self.model_import_path = 'django_app.models.Article'
        self.field_name = 'descripcion_nueva'
        self.operation = Elasticsearch_add_field(
            self.model_import_path, self.field_name )

        self.mock_model = Mock()
        self.index_name = 'some_test_index'
        self.mock_model._index._name = self.index_name

        self.mock_get_model = patch.object(
            self.operation, 'get_model', return_value=self.mock_model )
        self.mock_get_model.start()
        self.addCleanup( self.mock_get_model.stop )

    def mock_mapping_response( self, properties ):
        return {
            f'{self.index_name}': {
                'mappings': {
                    'properties': properties
                }
            }
        }

    def test_should_not_be_reversible( self ):
        self.assertFalse( self.operation.reversible )

    def test_should_not_reduce_to_sql( self ):
        self.assertFalse( self.operation.reduces_to_sql )

    def test_state_forwards_should_not_modify_state( self ):
        state = Mock()
        result = self.operation.state_forwards( 'django_app', state )
        self.assertIsNone( result )
        state.assert_not_called()

    def test_when_index_does_not_exist_should_raise( self ):
        self.mock_model._index.get_mapping.side_effect = NotFoundError(
            404, 'index_not_found_exception', {} )

        with self.assertRaises( Elasticsearch_index_not_found ):
            self.operation.database_forwards(
                'django_app', Mock(), None, None )

    def test_when_index_does_not_exist_exception_has_index_name( self ):
        self.mock_model._index.get_mapping.side_effect = NotFoundError(
            404, 'index_not_found_exception', {} )

        with self.assertRaises( Elasticsearch_index_not_found ) as ctx:
            self.operation.database_forwards(
                'django_app', Mock(), None, None )
        self.assertEqual( ctx.exception.index_name, self.index_name )

    def test_when_field_already_exists_should_not_call_save( self ):
        self.mock_model._index.get_mapping.return_value = (
            self.mock_mapping_response(
                { self.field_name: { 'type': 'text' } } )
        )

        self.operation.database_forwards(
            'django_app', Mock(), None, None )

        self.mock_model._index.save.assert_not_called()

    def test_when_field_does_not_exist_should_call_save( self ):
        self.mock_model._index.get_mapping.return_value = (
            self.mock_mapping_response( { 'otro_campo': { 'type': 'text' } } )
        )

        self.operation.database_forwards(
            'django_app', Mock(), None, None )

        self.mock_model._index.save.assert_called_once()

    def test_database_backwards_should_not_raise( self ):
        try:
            self.operation.database_backwards(
                'django_app', Mock(), None, None )
        except Exception as e:
            self.fail(
                f"database_backwards no deberia lanzar excepciones: {e}" )

    def test_database_backwards_should_not_modify_mapping( self ):
        self.operation.database_backwards(
            'django_app', Mock(), None, None )
        self.mock_model._index.save.assert_not_called()

    def test_describe_should_mention_field_and_model( self ):
        description = self.operation.describe()
        self.assertIn( self.field_name, description )
        self.assertIn( self.model_import_path, description )

    def test_deconstruct_should_return_correct_args( self ):
        path, args, kwargs = self.operation.deconstruct()
        self.assertEqual(
            path, 'Elasticsearch_add_field' )
        self.assertEqual(
            args, [ self.model_import_path, self.field_name ] )
        self.assertEqual( kwargs, {} )


class Test_elasticsearch_index_not_found_exception( TestCase ):
    def test_should_store_index_name( self ):
        self.index_name = 'some_test_index'
        exception = Elasticsearch_index_not_found( self.index_name )
        self.assertEqual( exception.index_name, self.index_name )

    def test_should_build_a_descriptive_message( self ):
        self.index_name = 'some_test_index'
        exception = Elasticsearch_index_not_found( self.index_name )
        self.assertIn( self.index_name, str( exception ) )
        self.assertIn( 'no existe', str( exception ) )
