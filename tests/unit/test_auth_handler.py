import pytest

from msgraph.core.middleware.authorization import AuthorizationHandler
from msgraph.core.middleware.request_context import RequestContext


def test_context_options_override_default_scopes():
    """ Test scopes found in the request context override default scopes"""
    default_scopes = ['.default']
    middleware_control = {
        'scopes': ['email.read'],
    }
    request_context = RequestContext(middleware_control, {})

    auth_handler = AuthorizationHandler(None, scopes=default_scopes)

    auth_handler_scopes = auth_handler.get_scopes(request_context)
    assert auth_handler_scopes == middleware_control['scopes']


def test_auth_handler_get_scopes_does_not_overwrite_default_scopes():
    default_scopes = ['.default']
    middleware_control = {
        'scopes': ['email.read'],
    }
    request_context = RequestContext(middleware_control, {})
    auth_handler = AuthorizationHandler(None, scopes=default_scopes)

    auth_handler_scopes = auth_handler.get_scopes(request_context)

    assert auth_handler.scopes == default_scopes
