class Elasticsearch_index_not_found( Exception ):
    """
    se lanza cuando no se encuentra un indice de elasticsearch

    Parameters
    ----------
    index_name: str
        nombre del indice que no fue encontrado

    Attributes
    ----------
    index_name: str
        nombre del indice que no fue encontrado
    """
    def __init__( self, index_name, *args ):
        self.index_name = index_name
        message = (
            f"el indice '{index_name}' no existe"
        )
        super().__init__( message, *args )


class Elasticsearch_reindex_count_mismatch( Exception ):
    """
    se lanza cuando el conteo de documentos despues de un reindex
    no coincide con el conteo del indice origen, indicando que la
    copia pudo haber sido incompleta

    Parameters
    ----------
    source_index: str
        indice origen
    dest_index: str
        indice destino
    source_count: int
        conteo de documentos en el origen
    dest_count: int
        conteo de documentos en el destino

    Attributes
    ----------
    source_index: str
    dest_index: str
    source_count: int
    dest_count: int
    """
    def __init__( self, source_index, dest_index, source_count, dest_count ):
        self.source_index = source_index
        self.dest_index = dest_index
        self.source_count = source_count
        self.dest_count = dest_count
        message = (
            f"el conteo de documentos no coincide al reindexar "
            f"'{source_index}' ({source_count}) -> "
            f"'{dest_index}' ({dest_count})"
        )
        super().__init__( message )
