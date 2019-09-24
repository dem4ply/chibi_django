import json
import logging

from chibi import madness
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


logger = logging.getLogger( 'chibi_django.models' )


class Chibi_model( models.Model ):
    id = models.CharField( _( "Id" ), max_length=64, primary_key=True )

    class Meta:
        abstract = True


@receiver( pre_save )
def chibi_model_create_pk( sender, instance, **kw ):
    if not instance.pk and issubclass( sender, Chibi_model ):
        model_meta = sender._meta
        max_length = model_meta.get_field( 'id' ).max_length
        start = max_length // 2
        max_retry = 5
        count_retry = 0
        while True:
            try_pk = madness.string.generate_token_b64( length=start )
            is_pk_exists = sender.objects.filter( pk=try_pk ).count()
            if is_pk_exists == 0:
                break
            logger.warinig(
                "colicion de pks",
                extra={
                    'number_pk_collide': 1, 'pk_collide': [ try_pk ],
                    'length_of_pk': start, 'count_of_retry': count_retry,
                    'max_length_pk': max_length,
                    'current_length': len( try_pk )
                } )
            if count_retry >= max_retry:
                start += 1
                count_retry += 1
                start = min( start, max_length )

        instance.pk = try_pk


class Header( models.Model ):
    key = models.CharField( max_length=128 )
    value_str = models.TextField( blank=True )

    class Meta:
        abstract = True

    def save( self, *args, **kw ):
        self.value = self.value
        super().save( *args, **kw )

    @property
    def value( self ):
        try:
            value = self._value
        except AttributeError:
            try:
                value = json.loads( self.value_str )
            except ( ValueError, TypeError ):
                value = self.value_str
        return value

    @value.setter
    def value( self, value ):
        if isinstance( value, str ):
            self.value_str = value
            self._value = value
        else:
            self.value_str = json.dumps( value )
            self._value = value

    def __str__( self ):
        return "{}: {}".format( self.key, self.value )

    def __repr__( self ):
        return "Header( key='{}' value={} )".format( self.key, self.value )

    def __eq__( self, other ):
        if not isinstance( other, Header ):
            return False
        return self.key == other.key and self.value == self.value
