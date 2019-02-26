from django.urls import path, include
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.test import TestCase, override_settings
import unittest
from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework import viewsets

from rest_framework import status
from rest_framework.response import Response

from chibi_user.authentication import Token_simple_authentication
from chibi_user.models import User as User_model, Token as Token_model
from chibi_django.view_set import Model_viewset

from rest_framework_nested import routers
from django.db import models
from rest_framework import serializers


factory = APIRequestFactory()


class Action( models.Model ):
    pass


class Action_serializer( serializers.ModelSerializer ):
    class Meta:
        model = Action
        fields = ( 'pk', )


from rest_framework.permissions import AllowAny


class Mock_View( Model_viewset ):
    permission_classes = ( AllowAny, )
    queryset = Action.objects.all()
    serializer_class = Action_serializer


router = routers.SimpleRouter()
router.register( r'', Mock_View, base_name='mock' )

urlpatterns = router.urls


@override_settings(
    ROOT_URLCONF='chibi_django.tests.integration.view_set' )
class Test_view_set( TestCase ):

    def test_list_should_return_200( self ):
        self.client = APIClient( enforce_csrf_checks=True )
        url = reverse( 'mock-list' )
        response = self.client.get( url )
        self.assertEqual( response.status_code, status.HTTP_200_OK )

    def test_list_create_should_return_201( self ):
        self.client = APIClient( enforce_csrf_checks=True )
        url = reverse( 'mock-list' )
        response = self.client.post( url )
        self.assertEqual( response.status_code, status.HTTP_201_CREATED )

    def test_detail_should_return_200( self ):
        self.client = APIClient( enforce_csrf_checks=True )
        a = Action.objects.create()
        url = reverse( 'mock-detail', kwargs={ 'pk': a.pk } )
        response = self.client.get( url )
        self.assertEqual( response.status_code, status.HTTP_200_OK )

    def test_delete_should_return_204( self ):
        self.client = APIClient( enforce_csrf_checks=True )
        a = Action.objects.create()
        url = reverse( 'mock-detail', kwargs={ 'pk': a.pk } )
        response = self.client.delete( url )
        self.assertEqual( response.status_code, status.HTTP_204_NO_CONTENT )

    def test_path_should_return_204( self ):
        self.client = APIClient( enforce_csrf_checks=True )
        a = Action.objects.create()
        url = reverse( 'mock-detail', kwargs={ 'pk': a.pk } )
        response = self.client.patch( url )
        self.assertEqual( response.status_code, status.HTTP_204_NO_CONTENT )

    def test_put_should_return_204( self ):
        self.client = APIClient( enforce_csrf_checks=True )
        a = Action.objects.create()
        url = reverse( 'mock-detail', kwargs={ 'pk': a.pk } )
        response = self.client.put( url )
        self.assertEqual( response.status_code, status.HTTP_204_NO_CONTENT )
