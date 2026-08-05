import logging

from chibi_donkey.donkey import Donkey
from elasticsearch.exceptions import NotFoundError

from .base import Elasticsearch_operation
from chibi_django.elasticsearch.exceptions import (
    Elasticsearch_index_not_found
)


logger = logging.getLogger( "chibi_django.elasticsearch.operations" )


class Elasticsearch_add_field( Elasticsearch_operation ):
    """
    Operation de Django para agregar un campo nuevo al mapping de
    un indice de Elasticsearch asociado a un modelo de
    elasticsearch-dsl.

    Solo actualiza el mapping si el campo aun no existe, evitando
    llamadas innecesarias a put_mapping().

    No es reversible: no quita el campo del indice pero no lanza la excepcion
    """

    reversible = True

    def __init__( self, model_import_path, field_name ):
        """
        Parameters
        ----------
        model_import_path: str
            path completo al modelo, ej. 'django_app.models.ES_model'
            (se guarda como string para que la migracion sea
            serializable y no dependa de importar el modelo en el
            momento de escribir la migracion)
        field_name: str
            nombre del campo que se espera agregar al mapping, usado
            solo para validar si ya existe antes de hacer put_mapping
        """
        super().__init__( model_import_path )
        self.field_name = field_name

    def get_mapping_or_raise( self, model ):
        try:
            return model._index.get_mapping()
        except NotFoundError as e:
            raise Elasticsearch_index_not_found( model._index._name ) from e

    def field_exists_in_mapping( self, model ):
        mapping = self.get_mapping_or_raise( model )

        for real_index, data in mapping.items():
            properties = data.get( 'mappings', {} ).get( 'properties', {} )
            donkey = Donkey( separator='.' )
            try:
                exists = donkey.get( self.field_name, properties )
            except KeyError:
                exists = False
            return exists
        return False

    def database_forwards(
            self, app_label, schema_editor, from_state, to_state ):
        model = self.get_model()

        if self.field_exists_in_mapping( model ):
            logger.info(
                f"el campo '{self.field_name}' ya existe en el "
                f"mapping de '{model._index._name}', no se modifica "
                "nada" )
            return

        logger.info(
            f"agregando el campo '{self.field_name}' al mapping de "
            f"'{model._index._name}'" )
        model._index.close()
        model._index.save()
        model._index.open()

    def database_backwards(
            self, app_label, schema_editor, from_state, to_state ):
        logger.warning(
            f"no es posible eliminar el campo '{self.field_name}' "
            f"del mapping de Elasticsearch, se omite la reversion" )

    def describe( self ):
        return (
            f"Agrega el campo '{self.field_name}' al mapping de "
            f"Elasticsearch para {self.model_import_path}" )

    def deconstruct( self ):
        return (
            self.__class__.__qualname__,
            [ self.model_import_path, self.field_name ],
            {},
        )
