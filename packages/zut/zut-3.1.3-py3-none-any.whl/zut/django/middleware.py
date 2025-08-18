from __future__ import annotations

import logging
import re
from types import FunctionType
from typing import Sequence

from asgiref.local import Local
from django.conf import settings
from django.contrib.auth.backends import RemoteUserBackend as BaseRemoteUserBackend
from django.contrib.auth.middleware import PersistentRemoteUserMiddleware as BasePersistentRemoteUserMiddleware
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.contrib.auth.views import LoginView, LogoutView, redirect_to_login
from django.http import HttpRequest, JsonResponse
from django.views.generic import RedirectView

try:
    from rest_framework.permissions import AllowAny as APIAllowAny
    from rest_framework.views import APIView
except ModuleNotFoundError:
    APIView = None
    APIAllowAny = None

_logger = logging.getLogger(__name__)


#region Thread

class ThreadLocalMiddleware:
    """
    Register request object as a local context/thread variable.
    
    This make it available to parts of Django that do not have direct access to the request,
    such as models (e.g. allows historization of the authenticated user making a change).
    """
    _local = Local()

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        self.__class__._local.request = request
        response = self.get_response(request)
        del self.__class__._local.request
        return response

    @classmethod
    def get_request_or_none(cls) -> HttpRequest|None:
        try:
            return cls._local.request
        except:
            return None # used from management command or CLI

    @classmethod
    def get_request(cls) -> HttpRequest:
        try:
            return cls._local.request
        except:
            raise ValueError("No request associated to the current thread")

    @classmethod
    def get_user(cls) -> AbstractUser|AnonymousUser:
        request = cls.get_request_or_none()
        if request is None:
            return AnonymousUser()        
        return request.user

#endregion


#region Authentication

class ExtractRemoteUserBackend(BaseRemoteUserBackend):
    extract: re.Pattern|str|Sequence[re.Pattern|str]|None = None
    """ First capture group is used as the username. Or REMOTE_USER_EXTRACT settings directive. """

    strip_prefix: str|Sequence[str]|None = None
    """ Or REMOTE_USER_STRIP_PREFIX settings directive. """

    strip_suffix: str|Sequence[str]|None = None
    """ Or REMOTE_USER_STRIP_SUFFIX settings directive. """

    _initialized = False
    _extract: Sequence[re.Pattern]
    _strip_prefix: Sequence[str]
    _strip_suffix: Sequence[str]

    def __init__(self, *args, **kwargs):
        self.ensure_initialized()
        super().__init__(*args, **kwargs)

    @classmethod
    def ensure_initialized(cls):
        if cls._initialized:
            return
        
        def normalize(values, env_name, converter = lambda value: value):
            if values is None:
                target_values = []
            elif isinstance(values, Sequence) and not isinstance(values, str):
                target_values = [converter(value) for value in values]
            else:
                target_values = [converter(values)]
            
            values = getattr(settings, env_name, None)
            if values:
                if not (isinstance(values, Sequence) and not isinstance(values, str)):
                    values = [values]
                for value in values:
                    value = converter(value)
                    if not value in target_values:
                        target_values.append(value)

            return target_values

        cls._extract = normalize(cls.extract, 'REMOTE_USER_EXTRACT', lambda value: value if isinstance(value, re.Pattern) else re.compile(value))
        
        cls._strip_prefix = normalize(cls.strip_prefix, 'REMOTE_USER_STRIP_PREFIX')
        cls._strip_prefix.sort(key=lambda v: -len(v))

        cls._strip_suffix = normalize(cls.strip_suffix, 'REMOTE_USER_STRIP_SUFFIX')
        cls._strip_suffix.sort(key=lambda v: -len(v))
    
    def clean_username(self, username: str):
        raw_username = username
        username = username.lower()

        for pattern in self._extract:
            m = pattern.match(username)
            if m:
                username = m[1]
                break

        for value in self._strip_prefix:
            if username.startswith(value):
                username = username[len(value):]
                break

        for value in self._strip_suffix:
            if username.endswith(value):
                username = username[:-len(value)]
                break

        _logger.debug("Raw remote user: %s, extracted: %s", raw_username, username)
        return username

class DebugRemoteUserMiddleware(BasePersistentRemoteUserMiddleware):
    _default_user: str|None = None
    _initialized = False

    def __call__(self, request):
        self.ensure_initialized()
        if self._default_user and not self.header in request.META:
            request.META[self.header] = self._default_user
        return super().__call__(request)

    @classmethod
    def ensure_initialized(cls):
        if cls._initialized:
            return
        if not settings.DEBUG:
            return
        cls._default_user = getattr(settings, 'DEBUG_REMOTE_USER', None)

#endregion


#region Authorization

class SuperUserAuthorizationMiddleware:
    """
    Restrict non-protected views to superuser.

    Views may be protected using an AccessMixin (standard class-based views)
    or with `permission_classes` attribute (Django Rest Framework API views).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        response = self.get_response(request)
        return response

    def process_view(self, request: HttpRequest, view_func, view_args, view_kwargs):        
        if settings.DEBUG and settings.MEDIA_URL != '/' and request.path.startswith(settings.MEDIA_URL):
            return
         
        try:
            view_class = view_func.view_class
            # Class-based view
            return self.process_view_class(request, view_class)
        except AttributeError:
            try:
                view_class = view_func.cls
                # API viewset (Django Rest Framework)
                return self.process_view_class(request, view_class)
            except AttributeError:
                # function-based view
                return self.process_view_func(request, view_func)
    
    def process_view_func(self, request: HttpRequest, view_func: FunctionType):
        """
        Process a function-based view.
        """
        if view_func.__module__ in {'django.views.static', 'import_export.admin'} or view_func.__module__.startswith(("django.contrib.", "")):
            return # ignore: use default visibility
        
        _logger.debug("Function-based view %s (%s) - using default authorization", f"{view_func.__module__}.{view_func.__name__}", request.path)
        if not self.is_authorized(request.user):
            return redirect_to_login(next=request.get_full_path())
        
    def process_view_class(self, request: HttpRequest, view_class: type):
        if request.path == '/':
            return # ignore
        
        elif issubclass(view_class, (LoginView, LogoutView, RedirectView)):
            return # ignore

        elif APIView and issubclass(view_class, APIView):
            # API view (Django Rest Framework)
            if not view_class.permission_classes or (view_class.permission_classes == [APIAllowAny] and not 'permission_classes' in view_class.__dict__):
                _logger.debug("API view class %s (%s) has no direct permission_classes - using default authorization", f"{view_class.__module__}.{view_class.__qualname__}", request.path)
                if not self.is_authorized(request.user):
                    return JsonResponse({"detail": "API permissions not properly configured."}, status=403)

        else:
            # Standard class-based view
            if not issubclass(view_class, AccessMixin):
                _logger.debug("View class %s (%s) has no AccessMixin - using default authorization", f"{view_class.__module__}.{view_class.__qualname__}", request.path)
                if not self.is_authorized(request.user):
                    return redirect_to_login(next=request.get_full_path())

    def is_authorized(self, user: AbstractUser|AnonymousUser):
        return user.is_superuser

#endregion
