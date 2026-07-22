from rest_framework import serializers
from elasticsearch_dsl import field as es_field


class ES_serializer( serializers.Serializer ):
    """
    Emula serializers.ModelSerializer pero para Documents de
    elasticsearch-dsl (Chibi_model / ES_chibi_model).

    Meta:
        model: el Document de elasticsearch-dsl (requerido)
        fields: lista de nombres a incluir, o '__all__' (default)
            '__all__' incluye pk, create_at, update_at + todos los
            campos definidos en el mapping del modelo
        exclude: lista de nombres a excluir (alternativa a 'fields')
        extra_kw : dict { nombre_campo: {kw extra para el field} }

    Campos Object/Nested (relaciones a InnerDoc) deben declararse
    explícitamente, igual que las relaciones en ModelSerializer:

        class ES_inner_doc( ES_serializer ):
            class Meta:
                model = ES_inner_doc_model

        class Article_list_serializer( ES_serializer ):
            inner_doc = ES_inner_doc()

            class Meta:
                model = ES_model
    """

    serializer_field_mapping = {
        es_field.Boolean: serializers.BooleanField,
        es_field.Date: serializers.DateTimeField,
        es_field.Float: serializers.FloatField,
        es_field.Double: serializers.FloatField,
        es_field.Integer: serializers.IntegerField,
        es_field.Long: serializers.IntegerField,
        es_field.Short: serializers.IntegerField,
        es_field.Byte: serializers.IntegerField,
        es_field.Keyword: serializers.CharField,
        es_field.Text: serializers.CharField,
    }

    def get_fields( self ):
        declared_fields = dict( self._declared_fields )
        meta = getattr( self, 'Meta', None )
        assert meta is not None, (
            f"{self.__class__.__name__} necesita una clase Meta"
        )
        model = getattr( meta, 'model', None )
        assert model is not None, (
            f"{self.__class__.__name__}.Meta necesita 'model'"
        )

        extra_kw = getattr( meta, 'extra_kw', {} )
        field_names = self._get_field_names( meta, model )

        fields = {}
        for name in field_names:
            if name in declared_fields:
                fields[ name ] = declared_fields[ name ]
                continue
            fields[ name ] = self._build_field(
                name, model, extra_kw.get( name, {} )
            )
        return fields

    def _get_field_names( self, meta, model ):
        exclude = set( getattr( meta, 'exclude', () ) )
        mapping_props = model._doc_type.mapping.properties.properties.to_dict()
        default_fields = [ 'pk', 'create_at', 'update_at' ] + list( mapping_props.keys() )

        fields = getattr( meta, 'fields', '__all__' )
        names = default_fields if fields == '__all__' else list( fields )

        return [ n for n in names if n not in exclude ]

    def _build_field( self, name, model, extra ):
        if name == 'pk':
            kw = { 'read_only': True }
            kw.update( extra )
            return serializers.CharField( **kw )

        if name in ( 'create_at', 'update_at' ):
            kw = { 'read_only': True }
            kw.update( extra )
            return serializers.DateTimeField( **kw )

        es_instance = model._doc_type.mapping.properties.properties[ name ]

        if isinstance( es_instance, ( es_field.Object, es_field.Nested ) ):
            raise TypeError(
                f"el campo '{name}' es Object/Nested, debes declararlo "
                f"explicitamente en el serializer con su propio "
                f"ES_serializer, igual que 'inner_doc' en el ejemplo"
            )

        for klass in type( es_instance ).__mro__:
            if klass in self.serializer_field_mapping:
                drf_field_class = self.serializer_field_mapping[ klass ]
                break
        else:
            raise TypeError(
                f"no se encontro un DRF field para el tipo "
                f"{type( es_instance )} del campo '{name}'. "
                f"Declaralo explicitamente o agrega el mapeo a "
                f"serializer_field_mapping"
            )

        return drf_field_class( **dict( extra ) )

    def create( self, validated_data ):
        meta = self.Meta
        model = meta.model
        instance = model( **validated_data )
        instance.save()
        return instance

    def update( self, instance, validated_data ):
        for attr, value in validated_data.items():
            setattr( instance, attr, value )
        instance.save()
        return instance

    def patch_doc_save( self, instance ):
        """
        Guarda solo los campos validados via partial update de
        Elasticsearch (document.update), en vez de reindexar el
        documento completo.

        Requiere que el serializer se haya instanciado con
        partial=True, ej:

        Retorna la instancia actualizada.

        Examples
        ========
        >>>serializer = MySerializer(
            instance, data=request.data, partial=True
        )
        >>>serializer.is_valid( raise_exception=True )
        >>>serializer.patch_doc_save( instance )
        """
        assert self.partial, (
            "patch_doc_save solo debe usarse con partial=True, "
            "para un update completo usa .save() normal"
        )
        assert hasattr( self, '_validated_data' ), (
            "debes llamar .is_valid() antes de patch_doc_save"
        )

        fields_to_update = {
            k: v for k, v in self._validated_data.items()
            if k not in ( 'pk', 'create_at', 'update_at' )
        }

        if not fields_to_update:
            return instance

        instance.update( **fields_to_update )
        return instance
