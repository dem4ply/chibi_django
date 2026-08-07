from unittest import TestCase
from unittest.mock import Mock, patch

from chibi_django.elasticsearch.operations.delete_index import (
    Elasticsearch_delete_index,
)


class Provider( Mock ):
    _index = Mock()


class Test_elasticsearch_delete_index_get_model( TestCase ):
    def test_without_suffix_should_return_the_base_model( self ):
        mock_base_model = Mock()
        operation = Elasticsearch_delete_index( 'app.models.Provider' )

        with patch.object(
                Elasticsearch_delete_index.__mro__[ 1 ], 'get_model',
                return_value=mock_base_model ):
            model = operation.get_model()

        self.assertIs( model, mock_base_model )

    def test_with_suffix_should_return_a_cloned_model_with_new_index_name(
            self ):
        mock_base_model = Provider
        mock_base_model._index._name = 'providers'
        mock_base_model._index.clone.return_value = Mock()

        operation = Elasticsearch_delete_index(
            'app.models.Provider', suffix='___migrating' )

        with patch.object(
                Elasticsearch_delete_index.__mro__[ 1 ], 'get_model',
                return_value=mock_base_model ):
            new_model = operation.get_model()

        self.assertEqual(
            new_model._index._name, 'providers___migrating' )


class Test_elasticsearch_delete_index_database_forwards( TestCase ):
    def test_should_delete_when_index_exists( self ):
        mock_model = Mock()
        mock_model._index.exists.return_value = True
        mock_model._index._name = 'providers'

        operation = Elasticsearch_delete_index( 'app.models.Provider' )
        operation.get_model = Mock( return_value=mock_model )

        operation.database_forwards(
            'app_label', Mock(), None, None )

        mock_model._index.delete.assert_called_once()

    def test_should_not_delete_when_index_does_not_exist( self ):
        mock_model = Mock()
        mock_model._index.exists.return_value = False

        operation = Elasticsearch_delete_index( 'app.models.Provider' )
        operation.get_model = Mock( return_value=mock_model )

        operation.database_forwards(
            'app_label', Mock(), None, None )

        mock_model._index.delete.assert_not_called()


class Test_elasticsearch_delete_index_describe( TestCase ):
    def test_should_mention_the_model_import_path( self ):
        operation = Elasticsearch_delete_index( 'app.models.Provider' )
        self.assertIn( 'app.models.Provider', operation.describe() )
