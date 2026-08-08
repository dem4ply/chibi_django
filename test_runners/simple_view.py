import factory
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from .snippet.response import (
    get_location,
    assert_has_location,
    assert_status_code,
    assert_data,
    assert_data_subset,
    assert_has_pages,
    assert_has_next_page,
)
from chibi.parser import link_header
from chibi_user.tests import get_superuser_test, get_user_test
from chibi_atlas import Chibi_atlas
from django.db import models


class API_test_case( APITestCase ):
    namespace = None
    name = None

    def reverse( self, action, *args, namespace=None, name=None, **kw ):
        if not self.namespace:
            raise ValueError( f"no se asigno {type(self)}.namespace" )
        if not self.name:
            raise ValueError( f"no se asigno {type(self)}.name" )

        result_nested = self.solve_nested_reverse( action, *args, **kw )
        if result_nested:
            kwargs = kw.setdefault( 'kwargs', {} )
            kwargs.update( result_nested )

        if namespace is None:
            namespace = self.namespace
        if name is None:
            name = self.name

        if action is None:
            return reverse(
                f'{namespace}:{name}', *args, **kw )

        return reverse(
            f'{namespace}:{name}-{action}', *args, **kw )

    def solve_nested_reverse( self, *args, **kw ):
        pass

    @property
    def list( self ):
        url = self.reverse( 'list' )
        return url

    @property
    def detail( self ):
        url = self.reverse( 'detail' )
        return url

    def list_of( self, pk, lookup='pk' ):
        if isinstance( pk, models.Model ):
            pk = pk.pk
        return self.reverse( 'list', kwargs={ lookup: pk } )

    def detail_of( self, pk, lookup='pk', kwargs=None ):
        if isinstance( pk, models.Model ):
            pk = pk.pk
        if kwargs is None:
            kwargs = { lookup: pk }
        else:
            kwargs[ lookup ] = pk
        return self.reverse( 'detail', kwargs=kwargs )

    def action_of( self, pk, name, lookup='pk', kwargs=None ):
        if isinstance( pk, models.Model ):
            pk = pk.pk
        if kwargs is None:
            kwargs = { lookup: pk }
        else:
            kwargs[ lookup ] = pk
        return self.reverse( name, kwargs=kwargs )

    def action( self, name, lookup='pk', kwargs=None ):
        return self.reverse( name, kwargs=kwargs )

    def get_location( self, response ):
        return get_location( response, client=self.client )

    def get_pages( self, response ):
        header = response[ "Link" ]
        links = link_header( header )
        return links

    def get_next_page( self, response ):
        header = response[ "Link" ]
        links = link_header( header )
        return self.client.get( links.next )

    def get_list( self, *args, **kw ):
        return self.client.get( self.list, *args, **kw )

    def get_detail_of( self, pk, lookup='pk', kwargs=None ):
        url = self.detail_of( pk, lookup=lookup, kwargs=kwargs )
        return self.client.get( url )

    def get_action_of( self, pk, name, lookup='pk', kwargs=None ):
        url = self.action_of( pk, name, lookup=lookup, kwargs=kwargs )
        return self.client.get( url )

    def post_list( self, *args, data=None, **kw ):
        return self.client.post( self.list, *args, data=data, **kw )

    def post_detail_of( self, pk, lookup='pk', data=None, kwargs=None ):
        url = self.detail_of( pk, lookup=lookup, kwargs=kwargs )
        return self.client.post( url, data=data )

    def post_action_of(
            self, pk, name, lookup='pk', data=None, format=None,
            kwargs=None ):
        url = self.action_of( pk, name, lookup=lookup, kwargs=kwargs )
        return self.client.post( url, data=data, format=format )

    def get_action(
            self, name, format=None, kwargs=None ):
        url = self.action( name, kwargs=kwargs )
        return self.client.get( url, format=format )

    def post_action(
            self, name, lookup='pk', data=None, format=None, kwargs=None ):
        url = self.action( name, lookup=lookup, kwargs=kwargs )
        return self.client.post( url, data=data, format=format )

    def patch_list( self, *args, data=None, **kw ):
        return self.client.patch( self.list, *args, data=data, **kw )

    def patch_detail_of( self, pk, lookup='pk', data=None, kwargs=None ):
        url = self.detail_of( pk, lookup=lookup, kwargs=kwargs )
        return self.client.patch( url, data=data )

    def delete_list( self, *args, data=None, **kw ):
        return self.client.delete( self.list, *args, data=data, **kw )

    def delete_detail_of( self, pk, lookup='pk', data=None, kwargs=None ):
        url = self.detail_of( pk, lookup=lookup, kwargs=kwargs )
        return self.client.delete( url, data=data )

    def assert_has_location( self, response ):
        return assert_has_location( response )

    def assert_has_page( self, response ):
        return assert_has_pages( response )

    def assert_has_next_page( self, response ):
        return assert_has_next_page( response )

    def assert_data( self, response, data, print_headers=False ):
        return assert_data(
            response, data, print_headers=print_headers )

    def assert_data_subset( self, response, data, print_headers=False ):
        return assert_data_subset(
            response, data, print_headers=print_headers )

    def assert_status_code( self, response, status ):
        return assert_status_code( response, status )

    def assert_response_is_200( self, response ):
        return self.assert_status_code( response, status.HTTP_200_OK )

    def assert_response_is_201( self, response ):
        return self.assert_status_code( response, status.HTTP_201_CREATED )

    def assert_response_is_204( self, response ):
        return self.assert_status_code( response, status.HTTP_204_NO_CONTENT )

    def build_data( self ):
        if hasattr( self, 'factory' ):
            return factory.build( Chibi_atlas, FACTORY_CLASS=self.factory, )
        raise NotImplementedError(
            "se nesesuita asignar self.factory o sobreescribir build_data"
        )


class Test_token_user( API_test_case ):

    def setUp( self ):
        super().setUp()
        self.password = 'password'
        self.client = self.client_class( enforce_csrf_checks=True )
        self.user, self.token = get_user_test()
        self.client.credentials( HTTP_AUTHORIZATION=str( self.token ) )


class Test_token_superuser( API_test_case ):

    def setUp( self ):
        super().setUp()
        self.password = 'password'
        self.client = self.client_class( enforce_csrf_checks=True )
        self.user, self.token = get_superuser_test()
        self.client.credentials( HTTP_AUTHORIZATION=str( self.token ) )
