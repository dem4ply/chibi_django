import logging
from chibi_elasticsearch.snippet import create_index_if_not_exists
from .base import Elasticsearch_operation


logger = logging.getLogger( "chibi_django.elasticsearch.operations" )


class Elasticsearch_index( Elasticsearch_operation ):
    """
    Operation de Django crear el índice
    de Elasticsearch asociado a un modelo de elasticsearch-dsl.

    Al revertir la migración, simplemente borra el índice.
    """

    reversible = True

    def database_forwards(
            self, app_label, schema_editor, from_state, to_state ):
        model = self.get_model()
        create_index_if_not_exists( model )

    def database_backwards(
            self, app_label, schema_editor, from_state, to_state ):
        model = self.get_model()
        if model._index.exists():
            logger.info(
                f"se encontro el indice '{model._index._name}' "
                "parando a eliminarlo" )
            model._index.delete()

    def describe( self ):
        return (
            "Recrea el índice de Elasticsearch "
            f"para {self.model_import_path}" )
