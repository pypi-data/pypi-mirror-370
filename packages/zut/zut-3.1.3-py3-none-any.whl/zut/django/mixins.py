"""
View mixins.
"""
from __future__ import annotations

from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

#region Authorization mixins

class UserPassesTestOrRedirectMixin(UserPassesTestMixin):
    request: HttpRequest
    
    def handle_no_permission(self):
        """
        Redirect to login page, even if the user is already authenticated: could display "You are logged in as xxx, but you are not authorized to access this page. Do you want to log in as another user?".
        (Default AccessMixin's handle_no_permission() method simply displays a 403 error in this situation).
        """
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(self.request.get_full_path())
    

class PermissionRequiredOrRedirectMixin(PermissionRequiredMixin):
    request: HttpRequest

    def handle_no_permission(self):
        """
        Redirect to login page, even if the user is already authenticated: could display "You are logged in as xxx, but you are not authorized to access this page. Do you want to log in as another user?".
        (Default AccessMixin's handle_no_permission() method simply displays a 403 error in this situation).
        """
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(next=self.request.get_full_path())


class AllowAnonymousMixin(UserPassesTestMixin):
    request: HttpRequest

    def test_func(self):
        return True


class IsAuthenticatedMixin(UserPassesTestMixin):
    request: HttpRequest

    def test_func(self):
        return self.request.user.is_authenticated


class IsStaffUserMixin(UserPassesTestOrRedirectMixin):
    request: HttpRequest

    def test_func(self):
        return self.request.user.is_staff


class IsSuperUserMixin(UserPassesTestOrRedirectMixin):
    request: HttpRequest

    def test_func(self):
        return self.request.user.is_superuser

#endregion
