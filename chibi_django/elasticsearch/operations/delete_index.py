import logging
from .base import Elasticsearch_operation


logger = logging.getLogger(
    "chibi_django.elasticsearch.operations.delete_index" )


class Elasticsearch_delete_index( Elasticsearch_operation ):
    """
    Operation de Django eliminar el indice
    """
    reversible = True

    def __init__( self, model_import_path, suffix=None ):
        """
        Parameters
        ----------
        model_import_path: str
            path completo al modelo, ej. 'django_app.models.ES_model'
        suffix: bool
            sufijo para el nombre del indice si no tiene usara el del modelo
        """
        super().__init__( model_import_path )
        self.suffix = suffix

    def get_model( self ):
        model = super().get_model()
        if self.suffix:
            new_model = type(
                f"{model.__qualname__}{self.suffix}", ( model, ), {} )
            new_model._index = model._index.clone()
            new_model._index._name = model._index._name + self.suffix
            return new_model
        return model

    def database_forwards(
            self, app_label, schema_editor, from_state, to_state ):
        model = self.get_model()
        if model._index.exists():
            logger.info(
                f"se encontro el indice '{model._index._name}' "
                "iniciando eliminacion" )
            model._index.delete()

    def describe( self ):
        return (
            "elimina el indice de Elasticsearch "
            f"para {self.model_import_path}" )
