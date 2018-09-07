from rest_framework import serializers
from chibi_user.models import Token as Token_model, User as User_model


class Token( serializers.ModelSerializer ):
    class Meta:
        model = Token_model
        fields = [ 'key', 'create_at' ]


class User( serializers.ModelSerializer ):
    token = Token( required=False )

    class Meta:
        model = User_model
        fields = [ 'pk', 'is_active', 'token' ]
        read_only_fields = [ 'pk', 'is_active', 'token' ]


class User_create( serializers.ModelSerializer ):
    class Meta:
        model = User_model
        fields = [ 'pk', 'url' ]
        read_only_fields = [ 'pk', 'url' ]
        extra_kwargs = {
            'url': { 'lookup_field': 'pk', 'view_name': 'users-detail' }
        }

    def create( self, validate_data ):
        user = User_model.objects.create()
        return user
