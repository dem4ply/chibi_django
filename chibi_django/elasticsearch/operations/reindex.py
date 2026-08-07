import logging

from chibi_elasticsearch.snippet import reindex_simple

from .base import Elasticsearch_operation
from chibi_django.elasticsearch.exceptions import (
    Elasticsearch_reindex_count_mismatch
)


logger = logging.getLogger( "chibi_django.elasticsearch.operations.reindex" )


class Elasticsearch_reindex( Elasticsearch_operation ):
    """
    operacion de django para ejecutar reindex a los indices
    """

    reversible = False

    def __init__(
            self, model_import_path, origin=False, dest=False,
            suffix='___migrating' ):
        """
        Parameters
        ----------
        model_import_path: str
            path completo al modelo, ej. 'django_app.models.ES_model'
        origin: bool
            define si el modelo es el origen
        origin: bool
            define si el modelo es el destino
        suffix: str
            sufijo usado para el nombre del indice temporal durante
            la migracion
        """
        super().__init__( model_import_path )
        self.origin = origin
        self.dest = dest
        if not dest and not origin:
            raise ValueError( "origin y dest no pueden ser ambas False" )
        self.suffix = suffix

    def reindex( self, es, source_index, dest_index ):
        response = reindex_simple( source_index, dest_index )
        failures = response.get( 'failures' )
        if failures:
            raise RuntimeError(
                f"fallaron {len( failures )} documentos al "
                f"reindexar '{source_index}' -> '{dest_index}': "
                f"{failures}"
            )
        logger.info(
            f"reindex completo: {response.get( 'total', 0 )} "
            f"documentos procesados, "
            f"{response.get( 'created', 0 )} creados"
        )
        self.verify_count( es, source_index, dest_index )
        return response

    def create_temp_index( self, es, name ):
        if es.indices.exists( index=name ):
            raise RuntimeError(
                f"el indice temporal '{name}' ya existia, "
                "se tiene que eliminar de manera manual" )
        es.indices.create( index=name )

    def verify_count( self, es, source_index, dest_index ):
        source_count = es.count( index=source_index )[ 'count' ]
        dest_count = es.count( index=dest_index )[ 'count' ]

        logger.info(
            f"verificando conteo: {source_index} = {source_count}, "
            f"{dest_index} = {dest_count}"
        )

        if source_count != dest_count:
            raise Elasticsearch_reindex_count_mismatch(
                source_index, dest_index, source_count, dest_count )

    def database_forwards(
            self, app_label, schema_editor, from_state, to_state ):
        model = self.get_model()
        es = model._get_connection()

        index_name = model._index._name
        temp_index_name = f"{index_name}{self.suffix}"
        if index_name == temp_index_name:
            raise RuntimeError(
                "el nombre del indice y el temporal no pueden ser el mismo" )

        if self.origin:
            self.create_temp_index( es, temp_index_name )
            self.reindex( es, index_name, temp_index_name )
        if self.dest:
            self.reindex( es, temp_index_name, index_name )

    def database_backwards(
            self, app_label, schema_editor, from_state, to_state ):
        logger.warning(
            f"no es posible revertir automaticamente la migracion "
            f"de mapping para '{self.model_import_path}', se omite "
            "la reversion"
        )

    def describe( self ):
        model = self.get_model()
        index_name = model._index._name
        temp_index_name = f"{index_name}{self.suffix}"

        if self.origin:
            return (
                f"migra los datos de {index_name} a {temp_index_name}"
            )
        if self.dest:
            return (
                f"migra los datos de {temp_index_name} a {index_name}"
            )
        raise NotImplementedError( "deberia de ser origin o dest" )
