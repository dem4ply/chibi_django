from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from .snippet.response import get_location
from django.db import models


class API_test_case( APITestCase ):
    namespace = None
    name = None

    def reverse( self, action, *args, **kw ):
        if not self.namespace:
            raise ValueError( f"no se asigno {type(self)}.namespace" )
        if not self.name:
            raise ValueError( f"no se asigno {type(self)}.name" )

        if action is None:
            return reverse(
                f'{self.namespace}:{self.name}', *args, **kw )

        return reverse(
            f'{self.namespace}:{self.name}-{action}', *args, **kw )

    @property
    def list( self ):
        url = self.reverse( 'list' )
        return url

    @property
    def detail( self ):
        url = self.reverse( 'detail' )
        return url

    def detail_of( self, pk ):
        if isinstance( pk, models.Model ):
            pk = pk.pk
        return self.reverse( 'detail', kwargs={ 'pk': pk } )

    def get_location( self, response ):
        return get_location( response, client=self.client )
