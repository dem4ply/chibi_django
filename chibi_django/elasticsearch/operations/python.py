import logging
from .base import Elasticsearch_operation


logger = logging.getLogger( "chibi_django.elasticsearch.operations.reindex" )


class Elasticsearch_run_python( Elasticsearch_operation ):
    """
    Ejecuta una funcion de python mandandole el modelo como parametro
    """

    reversible = True

    def __init__(
            self, model_import_path, func, reverse_func=None, suffix=None ):
        """
        Parameters
        ----------
        model_import_path: str
            path completo al modelo, ej. 'django_app.models.ES_model'
        value: bool
            valor del bloque
        """
        super().__init__( model_import_path )
        self.func = func
        self.reverse_func = reverse_func
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
        self.func( model )

    def database_backwards(
            self, app_label, schema_editor, from_state, to_state ):
        if self.reverse_func is None:
            raise NotImplementedError(
                "no se asigno una funcion de reversion" )
        self.reverse_func(from_state.apps, schema_editor)

    def describe( self ):
        return "ejecuta una funcion python"
