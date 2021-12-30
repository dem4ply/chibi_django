from django.db import models
from django.utils.translation import gettext_lazy as _
from chibi_django.models import Chibi_model
from .permission import Permission
from chibi_user.managers import Group_manager


class Group( Chibi_model ):
    """
    Groups are a generic way of categorizing users to apply permissions, or
    some other label, to those users. A user can belong to any number of
    groups.

    A user in a group automatically has all the permissions granted to that
    group. For example, if the group 'Site editors' has the permission
    can_edit_home_page, any user in that group will have that permission.

    Beyond permissions, groups are a convenient way to categorize users to
    apply some label, or extended functionality, to them. For example, you
    could create a group 'Special users', and you could write code that would
    do special things to those users -- such as giving them access to a
    members-only portion of your site, or sending them members-only email
    messages.
    """
    name = models.CharField( _( 'name' ), max_length=128, unique=True )
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_( 'permissions' ),
        blank=True,
    )

    objects = Group_manager()

    class Meta:
        verbose_name = _( 'group' )
        verbose_name_plural = _( 'groups' )

    def __str__( self ):
        return self.name

    def natural_key( self ):
        return ( self.name,)

