from unittest import TestCase
from unittest.mock import Mock, patch

from chibi_django.elasticsearch.exceptions import (
    Elasticsearch_reindex_count_mismatch,
)
from chibi_django.elasticsearch.operations import Elasticsearch_reindex


class Test_elasticsearch_reindex_init( TestCase ):
    def test_should_raise_when_origin_and_dest_are_both_false( self ):
        with self.assertRaises( ValueError ):
            Elasticsearch_reindex( 'app.models.Provider' )

    def test_should_not_raise_when_origin_is_true( self ):
        operation = Elasticsearch_reindex(
            'app.models.Provider', origin=True )
        self.assertTrue( operation.origin )
        self.assertFalse( operation.dest )

    def test_should_not_raise_when_dest_is_true( self ):
        operation = Elasticsearch_reindex(
            'app.models.Provider', dest=True )
        self.assertTrue( operation.dest )
        self.assertFalse( operation.origin )

    def test_should_use_default_suffix( self ):
        operation = Elasticsearch_reindex(
            'app.models.Provider', origin=True )
        self.assertEqual( operation.suffix, '___migrating' )

    def test_should_accept_custom_suffix( self ):
        operation = Elasticsearch_reindex(
            'app.models.Provider', origin=True, suffix='_temp' )
        self.assertEqual( operation.suffix, '_temp' )


class Test_elasticsearch_reindex_create_temp_index( TestCase ):
    def setUp( self ):
        self.operation = Elasticsearch_reindex(
            'app.models.Provider', origin=True )
        self.mock_es = Mock()

    def test_should_create_index_when_it_does_not_exist( self ):
        self.mock_es.indices.exists.return_value = False
        self.operation.create_temp_index( self.mock_es, 'providers_temp' )
        self.mock_es.indices.create.assert_called_once_with(
            index='providers_temp' )

    def test_should_raise_when_temp_index_already_exists( self ):
        self.mock_es.indices.exists.return_value = True
        with self.assertRaises( RuntimeError ):
            self.operation.create_temp_index( self.mock_es, 'providers_temp' )
        self.mock_es.indices.create.assert_not_called()


class Test_elasticsearch_reindex_verify_count( TestCase ):
    def setUp( self ):
        self.operation = Elasticsearch_reindex(
            'app.models.Provider', origin=True )
        self.mock_es = Mock()

    def test_should_not_raise_when_counts_match( self ):
        self.mock_es.count.side_effect = [
            { 'count': 10 }, { 'count': 10 } ]
        try:
            self.operation.verify_count(
                self.mock_es, 'providers', 'providers_temp' )
        except Exception as e:
            self.fail( f"no deberia lanzar excepcion: {e}" )

    def test_should_raise_when_counts_mismatch( self ):
        self.mock_es.count.side_effect = [
            { 'count': 10 }, { 'count': 7 } ]
        with self.assertRaises( Elasticsearch_reindex_count_mismatch ):
            self.operation.verify_count(
                self.mock_es, 'providers', 'providers_temp' )


class Test_elasticsearch_reindex_reindex_method( TestCase ):
    def setUp( self ):
        self.operation = Elasticsearch_reindex(
            'app.models.Provider', origin=True )
        self.mock_es = Mock()

    @patch(
        'chibi_django.elasticsearch.operations.reindex.reindex_simple' )
    def test_should_call_reindex_simple_and_verify_count(
            self, mock_reindex_simple ):
        mock_reindex_simple.return_value = {
            'total': 10, 'created': 10, 'failures': [] }
        self.mock_es.count.side_effect = [
            { 'count': 10 }, { 'count': 10 } ]

        self.operation.reindex( self.mock_es, 'providers', 'providers_temp' )

        mock_reindex_simple.assert_called_once_with(
            'providers', 'providers_temp' )

    @patch(
        'chibi_django.elasticsearch.operations.reindex.reindex_simple' )
    def test_should_raise_when_response_has_failures(
            self, mock_reindex_simple ):
        mock_reindex_simple.return_value = {
            'total': 10, 'created': 8,
            'failures': [ { 'id': '1', 'error': 'algo' } ]
        }
        with self.assertRaises( RuntimeError ):
            self.operation.reindex(
                self.mock_es, 'providers', 'providers_temp' )


class Test_elasticsearch_reindex_database_forwards( TestCase ):
    def setUp( self ):
        self.mock_model = Mock()
        self.mock_model._index._name = 'providers'
        self.mock_es = Mock()
        self.mock_model._get_connection.return_value = self.mock_es

    def test_should_raise_when_index_name_equals_temp_index_name( self ):
        operation = Elasticsearch_reindex(
            'app.models.Provider', origin=True, suffix='' )
        operation.get_model = Mock( return_value=self.mock_model )

        with self.assertRaises( RuntimeError ):
            operation.database_forwards(
                'app_label', Mock(), None, None )

    def test_origin_should_create_temp_index_and_reindex_forward( self ):
        operation = Elasticsearch_reindex(
            'app.models.Provider', origin=True )
        operation.get_model = Mock( return_value=self.mock_model )
        operation.create_temp_index = Mock()
        operation.reindex = Mock()

        operation.database_forwards(
            'app_label', Mock(), None, None )

        operation.create_temp_index.assert_called_once_with(
            self.mock_es, 'providers___migrating' )
        operation.reindex.assert_called_once_with(
            self.mock_es, 'providers', 'providers___migrating' )

    def test_dest_should_reindex_backward_without_creating_temp_index(
            self ):
        operation = Elasticsearch_reindex(
            'app.models.Provider', dest=True )
        operation.get_model = Mock( return_value=self.mock_model )
        operation.create_temp_index = Mock()
        operation.reindex = Mock()

        operation.database_forwards(
            'app_label', Mock(), None, None )

        operation.create_temp_index.assert_not_called()
        operation.reindex.assert_called_once_with(
            self.mock_es, 'providers___migrating', 'providers' )


class Test_elasticsearch_reindex_describe( TestCase ):
    def setUp( self ):
        self.mock_model = Mock()
        self.mock_model._index._name = 'providers'

    def test_should_describe_origin_migration( self ):
        operation = Elasticsearch_reindex(
            'app.models.Provider', origin=True )
        operation.get_model = Mock( return_value=self.mock_model )

        description = operation.describe()

        self.assertIn( 'providers', description )
        self.assertIn( 'providers___migrating', description )

    def test_should_describe_dest_migration( self ):
        operation = Elasticsearch_reindex(
            'app.models.Provider', dest=True )
        operation.get_model = Mock( return_value=self.mock_model )

        description = operation.describe()

        self.assertIn( 'providers___migrating', description )
        self.assertIn( 'providers', description )
