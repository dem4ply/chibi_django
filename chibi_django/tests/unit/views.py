# -*- coding: utf-8 -*-
import json

import xmltodict
import yaml
import unittest
from django.test import RequestFactory, TestCase

from chibi_django.views import page_not_found, server_error


class Test_error_handlers( TestCase ):
    """
    Pruebas para los handlers de error 404 y 500, verificando que
    la respuesta se serialice en el formato pedido por el cliente
    ( JSON, XML o YAML ) segun el header ``Accept``.
    """

    def setUp( self ):
        self.factory = RequestFactory()

    def test_page_not_found_should_return_404_status( self ):
        request = self.factory.get(
            '/no_existe/', HTTP_ACCEPT='application/json' )
        response = page_not_found( request, exception=None )
        self.assertEqual( response.status_code, 404 )

    def test_page_not_found_should_return_json_by_default( self ):
        request = self.factory.get(
            '/no_existe/', HTTP_ACCEPT='application/json' )
        response = page_not_found( request, exception=None )
        self.assertIn( 'application/json', response[ 'Content-Type' ] )

        body = json.loads( response.content )
        self.assertIn( 'detail', body )

    @unittest.skip( "no configurado para xml" )
    def test_page_not_found_should_return_xml_when_requested( self ):
        request = self.factory.get(
            '/no_existe/', HTTP_ACCEPT='application/xml' )
        response = page_not_found( request, exception=None )
        self.assertIn( 'application/xml', response[ 'Content-Type' ] )

        body = xmltodict.parse( response.content )
        self.assertIn( 'root', body )
        self.assertIn( 'detail', body[ 'root' ] )

    @unittest.skip( "no configurado para yaml" )
    def test_page_not_found_should_return_yaml_when_requested( self ):
        request = self.factory.get(
            '/no_existe/', HTTP_ACCEPT='application/yaml' )
        response = page_not_found( request, exception=None )
        self.assertIn( 'application/yaml', response[ 'Content-Type' ] )

        body = yaml.safe_load( response.content )
        self.assertIn( 'detail', body )

    @unittest.skip( "no configurado para text/plain" )
    def test_page_not_found_should_fallback_to_json_on_unknown_accept( self ):
        request = self.factory.get(
            '/no_existe/', HTTP_ACCEPT='text/plain' )
        response = page_not_found( request, exception=None )
        self.assertIn( 'application/json', response[ 'Content-Type' ] )

    def test_server_error_should_return_500_status( self ):
        request = self.factory.get(
            '/error/', HTTP_ACCEPT='application/json' )
        response = server_error( request )
        self.assertEqual( response.status_code, 500 )

    def test_server_error_should_return_json_by_default( self ):
        request = self.factory.get(
            '/error/', HTTP_ACCEPT='application/json' )
        response = server_error( request )
        self.assertIn( 'application/json', response['Content-Type'] )

        body = json.loads( response.content )
        self.assertIn( 'detail', body )

    @unittest.skip( "no configurado para xml" )
    def test_server_error_should_return_xml_when_requested( self ):
        request = self.factory.get(
            '/error/', HTTP_ACCEPT='application/xml' )
        response = server_error( request )
        self.assertIn( 'application/xml', response['Content-Type'] )

        body = xmltodict.parse( response.content )
        self.assertIn( 'root', body )
        self.assertIn( 'detail', body[ 'root' ] )

    @unittest.skip( "no configurado para yaml" )
    def test_server_error_should_return_yaml_when_requested( self ):
        request = self.factory.get(
            '/error/', HTTP_ACCEPT='application/yaml' )
        response = server_error( request )
        self.assertIn( 'application/yaml', response['Content-Type'] )

        body = yaml.safe_load( response.content )
        self.assertIn( 'detail', body )
