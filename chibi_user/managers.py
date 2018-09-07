from django.contrib.auth.models import BaseUserManager
from chibi import madness
from chibi_django.managers import Base_64_pk



class User_manager( Base_64_pk, BaseUserManager ):

    def create( self, *args, **kw ):
        user = super().create( *args, **kw )
        user.refresh_token()
        return user

    def create_user( self, *args, **kw  ):
        """
        Crea un usuario sin privilegios especiales
        """
        user = self.create( *args, **kw )
        return user

    def create_superuser( self, *args, **kw ):
        """
        Crea un superusuario
        """
        user = self.create_user(
            *args, is_staff=True, is_superuser=True, **kw )
        return user

    def create_user_test( self, *args, username=None, password=None, **kw ):
        """
        Crea un usuario para pruebas
        """
        if not username:
            username = madness.string.generate_string()
        if not password:
            password = 'password'
        user = self.create_user(
            *args, username=username, password=password, **kw )
        return user

    def create_superuser_test(
            self, *args, username=None, password=None, **kw ):
        """
        Crea un super usuairo para las pruebas
        """
        if not username:
            username = madness.string.generate_string()
        if not password:
            password = 'password'
        user = self.create_superuser(
            *args, username=username, password=password, **kw )
        return user
