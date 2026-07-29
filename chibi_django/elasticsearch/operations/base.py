import logging
from django.db.migrations.operations.base import Operation


logger = logging.getLogger( "chibi_django.elasticsearch.operations" )


class Elasticsearch_operation( Operation ):
    """
    Operation de Django para elasticsearch-dsl
    """

    reduces_to_sql = False
    reversible = False

    def __init__( self, model_import_path ):
        """
        Parameters
        ----------
        model_import_path: str
            path completo al modelo, ej. 'django_app.models.ES_model'
            (se guarda como string para que la migracion sea
            serializable y no dependa de importar el modelo en el
            momento de escribir la migracion)
        """
        self.model_import_path = model_import_path

    def get_model( self ):
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
        raise NotImplementedError

    def database_backwards(
            self, app_label, schema_editor, from_state, to_state ):
        raise NotImplementedError

    def describe( self ):
        raise NotImplementedError

    def deconstruct( self ):
        return (
            self.__class__.__qualname__,
            [ self.model_import_path ],
            {},
        )
