from django.db import models
from django.utils.translation import gettext_lazy as _
from chibi_user.user_base import User_base
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone


class User( User_base ):
    class Meta( User_base.Meta ):
        swappable = 'AUTH_USER_MODEL'
