from unittest import TestCase
from unittest.mock import Mock, patch

from chibi_django.elasticsearch.operations.python import (
    Elasticsearch_run_python,
)


class Provider( Mock ):
    _index = Mock()


class Test_elasticsearch_run_python_get_model( TestCase ):
    def test_without_suffix_should_return_the_base_model( self ):
        mock_base_model = Mock()
        operation = Elasticsearch_run_python(
            'app.models.Provider', func=lambda m: None )
        operation._get_model = Mock( return_value=mock_base_model )

        with patch.object(
                Elasticsearch_run_python.__mro__[ 1 ], 'get_model',
                return_value=mock_base_model ):
            model = operation.get_model()

        self.assertIs( model, mock_base_model )

    def test_with_suffix_should_return_a_cloned_model_with_new_index_name(
            self ):
        mock_base_model = Provider
        mock_base_model._index._name = 'providers'
        mock_base_model._index.clone.return_value = Mock()

        operation = Elasticsearch_run_python(
            'app.models.Provider', func=lambda m: None,
            suffix='___migrating' )

        with patch.object(
                Elasticsearch_run_python.__mro__[ 1 ], 'get_model',
                return_value=mock_base_model ):
            new_model = operation.get_model()

        self.assertEqual(
            new_model._index._name, 'providers___migrating' )
        self.assertTrue( issubclass( new_model, mock_base_model ) )


class Test_elasticsearch_run_python_database_forwards( TestCase ):
    def test_should_call_func_with_the_resolved_model( self ):
        mock_model = Mock()
        mock_func = Mock()
        operation = Elasticsearch_run_python(
            'app.models.Provider', func=mock_func )
        operation.get_model = Mock( return_value=mock_model )

        operation.database_forwards(
            'app_label', Mock(), None, None )

        mock_func.assert_called_once_with( mock_model )


class Test_elasticsearch_run_python_describe( TestCase ):
    def test_should_return_a_generic_description( self ):
        operation = Elasticsearch_run_python(
            'app.models.Provider', func=lambda m: None )
        self.assertEqual( operation.describe(), 'ejecuta una funcion python' )


class Test_elasticsearch_run_python_database_backwards( TestCase ):
    def test_should_raise_when_no_reverse_func_was_given( self ):
        operation = Elasticsearch_run_python(
            'app.models.Provider', func=lambda m: None )

        with self.assertRaises( NotImplementedError ):
            operation.database_backwards(
                'app_label', Mock(), Mock(), None )

    def test_should_call_reverse_func_with_apps_and_schema_editor( self ):
        mock_reverse_func = Mock()
        mock_from_state = Mock()
        mock_schema_editor = Mock()

        operation = Elasticsearch_run_python(
            'app.models.Provider', func=lambda m: None,
            reverse_func=mock_reverse_func )

        operation.database_backwards(
            'app_label', mock_schema_editor, mock_from_state, None )

        mock_reverse_func.assert_called_once_with(
            mock_from_state.apps, mock_schema_editor )
