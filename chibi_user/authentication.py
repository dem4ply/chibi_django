from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header, BaseAuthentication
from chibi_user.models import Token

__all__ = [ 'Token_simple_authentication' ]


class Token_simple_authentication( BaseAuthentication ):
    model = Token

    def authenticate( self, request ):
        auth = get_authorization_header( request ).split( b';' )
        if not auth:
            return None
        if len( auth ) == 1 and not auth[0]:
            return None

        auth = self.parse_tokens( auth )

        if len( auth ) == 0:
            msg = _( 'Invalid token header. No credentials provided.' )
            raise exceptions.AuthenticationFailed( msg )

        return self.authenticate_credentials( auth, request )

    def authenticate_credentials( self, tokens, request ):
        try:
            key = tokens.pop( 'Token' )
            token = self.model.objects.select_related( 'user' ).get( key=key )
        except ( KeyError, self.model.DoesNotExist ):
            raise exceptions.AuthenticationFailed( _( 'Invalid token.' ) )

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(
                _( 'User inactive or deleted.' ) )

        return ( token.user, token )

    def authenticate_header(self, request):
        return 'Token'

    def parse_tokens( self, tokens ):
        result = {}
        for token in tokens:
            if len( token ) == 0:
                msg = _( 'Invalid token header. No credentials provided.' )
                raise exceptions.AuthenticationFailed( msg )
            s_token = token.split()
            len_s_token = len( s_token )
            if len_s_token == 1 or len_s_token > 2:
                msg = _(
                    'Invalid token header. Token string '
                    'should not contain spaces.' )
                raise exceptions.AuthenticationFailed( msg )
            try:
                result[ s_token[0].decode() ] = s_token[1].decode()
            except UnicodeError:
                msg = _(
                    'Invalid token header. Token string '
                    'should not contain invalid characters.' )
                raise exceptions.AuthenticationFailed( msg )
        return result

    def check_prefix(self, prefix):
        return 'token' if prefix == 'token' else None
