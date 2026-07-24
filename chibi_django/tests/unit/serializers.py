import unittest
from rest_framework import serializers
from unittest.mock import Mock
from chibi_django.serializers import ES_serializer
from chibi_elasticsearch import Chibi_model as ES_chibi_model
from chibi_elasticsearch.unittests import patch_doc_save
from elasticsearch_dsl import InnerDoc, field


class Test_inner_model( InnerDoc ):
    name = field.Keyword()


class Test_model( ES_chibi_model ):
    inner_obj = field.Object( Test_inner_model )
    another_field = field.Keyword()
    some_int = field.Integer()


class Test_inner_model_serializer( ES_serializer ):
    class Meta:
        model = Test_inner_model


class Test_serializer_model( ES_serializer ):
    inner_obj = Test_inner_model_serializer()
    url = serializers.URLField()

    class Meta:
        model = Test_model


class Test_es_serializer( unittest.TestCase ):
    def test_auto_generates_char_fields( self ):
        class Serializer( ES_serializer ):
            inner_obj = serializers.DictField()  # placeholder para el Object

            class Meta:
                model = Test_model

        s = Serializer()
        fields = s.fields

        self.assertIsInstance(
            fields[ 'another_field' ], serializers.CharField )

    def test_pk_and_dates_are_read_only( self ):
        class Serializer( ES_serializer ):
            inner_obj = serializers.DictField()

            class Meta:
                model = Test_model

        s = Serializer()
        self.assertTrue( s.fields[ 'pk' ].read_only )
        self.assertTrue( s.fields[ 'create_at' ].read_only )
        self.assertTrue( s.fields[ 'update_at' ].read_only )
        self.assertIsInstance(
            s.fields[ 'update_at' ], serializers.DateTimeField )

    def test_explicit_field_overrides_auto( self ):
        class Serializer( ES_serializer ):
            inner_obj = serializers.DictField()
            another_field = serializers.FloatField()

            class Meta:
                model = Test_model

        s = Serializer()
        self.assertIsInstance(
            s.fields[ 'another_field' ], serializers.FloatField )

    def test_object_field_without_declaration_raises( self ):
        class Serializer( ES_serializer ):
            class Meta:
                model = Test_model

        s = Serializer()
        with self.assertRaises( TypeError ):
            s.fields

    def test_fields_meta_limits_fields( self ):
        class Serializer( ES_serializer ):
            class Meta:
                model = Test_model
                fields = [ 'pk', 'another_field' ]

        s = Serializer()
        self.assertEqual(
            set( s.fields.keys() ),
            { 'pk', 'another_field' } )

    def test_exclude_meta_removes_fields( self ):
        class Serializer( ES_serializer ):
            inner_obj = serializers.DictField()

            class Meta:
                model = Test_model
                exclude = [ 'another_field' ]

        s = Serializer()
        self.assertNotIn( 'another_field', s.fields )
        self.assertIn( 'pk', s.fields )

    @patch_doc_save
    def test_create_should_call_ES_save( self, save ):
        class Serializer( ES_serializer ):
            class Meta:
                model = Test_model
                exclude = [ 'inner_obj', 'some_int' ]

        s = Serializer( data={ 'another_field': "otro campo" } )
        self.assertTrue( s.is_valid( raise_exception=True ) )
        s.save()
        save.assert_called_once()

    @patch_doc_save
    def test_create_should_return_the_expected_model( self, save ):
        class Serializer( ES_serializer ):
            class Meta:
                model = Test_model
                exclude = [ 'inner_obj', 'some_int' ]

        s = Serializer( data={ 'another_field': "otro campo" } )
        self.assertTrue( s.is_valid( raise_exception=True ) )
        model = s.save()
        self.assertIsInstance( model, Test_model )
        self.assertEqual( model.another_field, "otro campo" )
        self.assertTrue( model.create_at )
        self.assertTrue( model.update_at )


class TestPatchDocSave( unittest.TestCase ):
    class Serializer( ES_serializer ):
        class Meta:
            model = Test_model
            exclude = [ 'inner_obj' ]

    def _make_serializer( self, validated_data, partial=True ):
        serializer = self.Serializer( partial=partial )
        serializer._validated_data = validated_data
        return serializer

    def test_patch_calls_update_with_validated_fields( self ):
        instance = Mock()
        serializer = self._make_serializer( {
            'another_field': 'nuevo nombre',
            'some_int': '100',
        } )

        serializer.patch_doc_save( instance )
        instance.update.assert_called_once_with(
            another_field='nuevo nombre', some_int='100' )

    def test_patch_excludes_readonly_fields( self ):
        instance = Mock()
        serializer = self._make_serializer({
            'pk': 'abc123',
            'create_at': 'ignored',
            'update_at': 'ignored',
            'another_field': 'nuevo nombre',
        })

        serializer.patch_doc_save( instance )
        instance.update.assert_called_once_with(
            another_field='nuevo nombre' )

    def test_patch_skips_update_call_when_no_fields( self ):
        instance = Mock()
        serializer = self._make_serializer( {
            'pk': 'abc123'
        } )

        result = serializer.patch_doc_save( instance )
        instance.update.assert_not_called()
        self.assertIs( result, instance )

    def test_patch_without_partial_raises( self ):
        instance = Mock()
        serializer = self._make_serializer( {
            'name': 'x'
        }, partial=False )

        with self.assertRaises( AssertionError ):
            serializer.patch_doc_save( instance )

    def test_patch_without_is_valid_raises( self ):
        instance = Mock()
        serializer = self.Serializer( partial=True )
        # no se llamó is_valid, no hay _validated_data

        with self.assertRaises( AssertionError ):
            serializer.patch_doc_save( instance )


class Multi_test_model( ES_chibi_model ):
    """
    modelo de prueba, solo para verificar el comportamiento de
    _build_field con campos multi y no-multi
    """
    name = field.Text( multi=False )
    inner_urls = field.Text( multi=True )
    tags = field.Keyword( multi=True )

    class Index:
        name = 'test__multi_test_model'


class Multi_test_serializer( ES_serializer ):
    class Meta:
        model = Multi_test_model


class Test_build_field_multi( unittest.TestCase ):

    def setUp( self ):
        self.serializer = Multi_test_serializer()
        self.model = Multi_test_model

    def test_multi_text_field_becomes_list_field( self ):
        result = self.serializer._build_field(
            'inner_urls', self.model, {}
        )
        self.assertIsInstance( result, serializers.ListField )
        self.assertIsInstance( result.child, serializers.CharField )

    def test_multi_keyword_field_becomes_list_field_with_correct_child( self ):
        result = self.serializer._build_field(
            'tags', self.model, {}
        )
        self.assertIsInstance( result, serializers.ListField )
        self.assertIsInstance( result.child, serializers.CharField )

    def test_non_multi_field_is_not_wrapped_in_list( self ):
        result = self.serializer._build_field(
            'name', self.model, {}
        )
        self.assertNotIsInstance( result, serializers.ListField )
        self.assertIsInstance( result, serializers.CharField )

    def test_multi_field_passes_extra_kwargs_to_list_field( self ):
        result = self.serializer._build_field(
            'inner_urls', self.model, { 'required': False }
        )
        self.assertIsInstance( result, serializers.ListField )
        self.assertFalse( result.required )

    def test_get_fields_generates_list_field_automatically( self ):
        fields = self.serializer.get_fields()
        self.assertIsInstance( fields[ 'inner_urls' ], serializers.ListField )
        self.assertIsInstance( fields[ 'tags' ], serializers.ListField )
        self.assertIsInstance( fields[ 'name' ], serializers.CharField )


class Multi_object_test_model( ES_chibi_model ):
    """
    modelo de prueba para el caso Object + multi=True, que debe
    seguir siendo rechazado por _build_field sin importar multi
    """
    inner_obj = field.Object( multi=True )

    class Index:
        name = 'test__multi_object_test_model'


class Multi_object_test_serializer( ES_serializer ):
    class Meta:
        model = Multi_object_test_model
        fields = [ 'inner_obj' ]


class Test_build_field_object_multi_still_raises( unittest.TestCase ):

    def test_multi_object_field_still_raises_before_checking_multi( self ):
        serializer = Multi_object_test_serializer()
        with self.assertRaises( TypeError ):
            serializer._build_field(
                'inner_obj', Multi_object_test_model, {}
            )
