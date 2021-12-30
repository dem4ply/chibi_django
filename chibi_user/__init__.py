from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured


def get_token_model():
    """
    Return the User model that is active in this project.
    """
    try:
        return django_apps.get_model(
            settings.AUTH_TOKEN_MODEL, require_ready=False )
    except ValueError:
        raise ImproperlyConfigured(
            "AUTH_TOKEN_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "AUTH_TOKEN_MODEL refers to model "
            "'%s' that has not been installed" % settings.AUTH_TOKEN_MODEL
        )
