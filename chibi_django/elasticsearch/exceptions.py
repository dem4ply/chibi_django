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
