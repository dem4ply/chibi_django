import logging
from django.db.migrations.operations.base import Operation
from chibi_elasticsearch.snippet import create_index_if_not_exists


logger = logging.getLogger( "chibi_django.elasticsearch.operations" )


class Elasticsearch_index( Operation ):
    """
    Operation de Django crear el índice
    de Elasticsearch asociado a un modelo de elasticsearch-dsl.

    Al revertir la migración, simplemente borra el índice.
    """

    reduces_to_sql = False
    reversible = True

    def __init__( self, model_import_path ):
        """
        model_import_path: str
            path completo al modelo, ej. 'django_app.models.ES_model'
            (se guarda como string para que la migración sea serializable
            y no dependa de importar el modelo en el momento de escribir
            la migración)
        """
        self.model_import_path = model_import_path

    def _get_model( self ):
        module_path, class_name = self.model_import_path.rsplit( '.', 1 )
        logger.info(
            f"importando el modelo {module_path}.{class_name}" )
        module = __import__( module_path, fromlist=[ class_name ] )
        return getattr( module, class_name )

    def state_forwards( self, app_label, state ):
        # no afecta el estado de los modelos de Django, solo Elasticsearch
        pass

    def database_forwards(
            self, app_label, schema_editor, from_state, to_state ):
        model = self._get_model()
        create_index_if_not_exists( model )

    def database_backwards(
            self, app_label, schema_editor, from_state, to_state ):
        model = self._get_model()
        if model._index.exists():
            logger.info(
                f"se encontro el indice '{model._index._name}' "
                "parando a eliminarlo" )
            model._index.delete()

    def describe( self ):
        return (
            "Recrea el índice de Elasticsearch "
            f"para {self.model_import_path}" )

    def deconstruct( self ):
        return (
            self.__class__.__qualname__,
            [ self.model_import_path ],
            {},
        )
