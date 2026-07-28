from django import http
from django.utils.translation import gettext as _
from chibi_django.exceptions import Http_not_found, Http_internal_server_error
from rest_framework.renderers import JSONRenderer


from rest_framework.request import Request
from rest_framework.settings import api_settings
from rest_framework.negotiation import DefaultContentNegotiation

from chibi_django.exceptions import Http_not_found, Http_internal_server_error


def _build_error_response( request, exception_instance, response_class ):
    """
    Arma una respuesta de error usando el mismo mecanismo de
    negociacion de contenido configurado en ``REST_FRAMEWORK``,

    Parameters
    ----------
    request : django.http.HttpRequest
        Request original recibido por el handler de Django.
    exception_instance : chibi_django.exceptions.Http_exception
        Instancia de la excepcion que contiene el ``context`` a
        serializar en el body de la respuesta.
    response_class : type
        Clase de respuesta de Django a instanciar
        (por ejemplo ``http.HttpResponseNotFound`` o
        ``http.HttpResponseServerError``).

    Returns
    -------
    django.http.HttpResponse
        Instancia de ``response_class`` con el body ya serializado
        en el formato negociado y el ``content_type`` correspondiente.
    """
    drf_request = Request( request )

    renderer_classes = [
        renderer_class()
        for renderer_class in api_settings.DEFAULT_RENDERER_CLASSES
    ]

    negotiator = DefaultContentNegotiation()
    format_suffix = drf_request.query_params.get(
        api_settings.URL_FORMAT_OVERRIDE
    )

    renderer, media_type = negotiator.select_renderer(
        drf_request, renderer_classes, format_suffix )

    data = exception_instance.context
    content = renderer.render(
        data, media_type, renderer_context={ 'request': drf_request } )

    return response_class( content, content_type=media_type )


def page_not_found(request, exception, template_name='404.html'):
    """
    Handler de error 404.

    Returns
    -------
    django.http.HttpResponseNotFound
        Respuesta con status 404 y el body serializado en el
        formato negociado.
    """
    base_exception = Http_not_found( _( "The resource does not exist." ) )
    return _build_error_response(
        request, base_exception, http.HttpResponseNotFound )


def server_error(request, template_name='500.html'):
    """
    Handler de error 500.

    Returns
    -------
    django.http.HttpResponseServerError
        Respuesta con status 500 y el body serializado en el
        formato negociado.
    """
    base_exception = Http_internal_server_error(
        _( "Internal server error." ) )
    return _build_error_response(
        request, base_exception, http.HttpResponseServerError )
