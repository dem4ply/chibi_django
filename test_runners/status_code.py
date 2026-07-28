import factory
from rest_framework import status
from chibi_atlas import Chibi_atlas

from test_runners.snippet.response import assert_status_code
from test_runners.simple_view import API_test_case


class Test_status_code( API_test_case ):
    expected_status_code = status.HTTP_200_OK


class Test_list( Test_status_code ):
    def test_list( self ):
        response = self.get_list()
        assert_status_code( response, self.expected_status_code )

    def get_url_kw( self ):
        raise NotImplementedError


class Test_retrieve( Test_status_code ):
    def test_retrieve( self ):
        if not hasattr( self, 'pk' ):
            raise NotImplementedError(
                "se nesecita asignar self.pk para el view"
            )
        response = self.get_detail_of( self.pk )
        assert_status_code( response, self.expected_status_code )


class Test_create( Test_status_code ):
    expected_create_status_code = status.HTTP_201_CREATED

    def test_create( self ):
        data = self.build_data()
        response = self.post_list( data=data )
        assert_status_code( response, self.expected_create_status_code )

    def build_data( self ):
        if hasattr( self, 'factory' ):
            return factory.build( Chibi_atlas, FACTORY_CLASS=self.factory, )
        raise NotImplementedError(
            "se nesesuita asignar self.factory o sobreescribir build_data"
        )
