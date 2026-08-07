from unittest import TestCase
from unittest.mock import Mock

from chibi_django.elasticsearch.operations.block_write import (
    Elasticsearch_block_write,
)


class Test_elasticsearch_block_write_set_block_on_model( TestCase ):
    def test_should_call_put_settings_with_true( self ):
        mock_model = Mock()
        mock_model._index._name = 'providers'

        operation = Elasticsearch_block_write(
            'app.models.Provider', True )
        operation.get_model = Mock( return_value=mock_model )

        operation.set_block_on_model()

        mock_model._index.put_settings.assert_called_once_with(
            body={ 'index.blocks.write': True } )

    def test_should_call_put_settings_with_false( self ):
        mock_model = Mock()
        mock_model._index._name = 'providers'

        operation = Elasticsearch_block_write(
            'app.models.Provider', False )
        operation.get_model = Mock( return_value=mock_model )

        operation.set_block_on_model()

        mock_model._index.put_settings.assert_called_once_with(
            body={ 'index.blocks.write': False } )


class Test_elasticsearch_block_write_database_forwards( TestCase ):
    def test_should_delegate_to_set_block_on_model( self ):
        operation = Elasticsearch_block_write(
            'app.models.Provider', True )
        operation.set_block_on_model = Mock()

        operation.database_forwards(
            'app_label', Mock(), None, None )

        operation.set_block_on_model.assert_called_once()


class Test_elasticsearch_block_write_describe( TestCase ):
    def test_should_describe_blocking_when_value_is_true( self ):
        operation = Elasticsearch_block_write(
            'app.models.Provider', True )
        description = operation.describe()
        self.assertIn( 'bloquendo', description )
        self.assertIn( 'app.models.Provider', description )

    def test_should_describe_unblocking_when_value_is_false( self ):
        operation = Elasticsearch_block_write(
            'app.models.Provider', False )
        description = operation.describe()
        self.assertIn( 'desbloquendo', description )
