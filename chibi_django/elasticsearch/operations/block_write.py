import logging
from .base import Elasticsearch_operation


logger = logging.getLogger( "chibi_django.elasticsearch.operations.reindex" )


class Elasticsearch_block_write( Elasticsearch_operation ):
    """
    Operacion para iniciar o terminar un bloqueo de escributra en un indice
    """

    reversible = True

    def __init__( self, model_import_path, value ):
        """
        Parameters
        ----------
        model_import_path: str
            path completo al modelo, ej. 'django_app.models.ES_model'
        value: bool
            valor del bloque
        """
        super().__init__( model_import_path )
        self.value = value

    def set_block_on_model( self ):
        model = self.get_model()
        if self.value:
            logger.info(
                "bloquiando la escritura en "
                f"el indice {model._index._name}" )
        else:
            logger.info(
                "desbloquiando la escritura en "
                f"el indice {model._index._name}" )
        model._index.put_settings(
            body={ 'index.blocks.write': self.value }  )

    def database_forwards(
            self, app_label, schema_editor, from_state, to_state ):
        self.set_block_on_model()

    def describe( self ):
        if self.value:
            return (
                f"bloquendo el modelo {self.model_import_path} "
                "para escrituras"
            )
        return (
            f"desbloquendo el modelo {self.model_import_path} "
            "para escrituras"
        )
