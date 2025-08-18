"""
Utilities for commands (in particular during initialization / seeding).
"""
from __future__ import annotations

import logging
import os
from importlib import import_module
from time import sleep
from typing import Any, Sequence

from zut import DelayedStr, Secret, SecretNotFound, is_secret_defined

from django.apps import AppConfig, apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.management.base import BaseCommand, CommandParser
from django.db.models import DateField, Field, GeneratedField, Model  # type: ignore

_logger = logging.getLogger(__name__)


#region Create or update users

def ensure_superuser(username: str|None = None, *,
                     email: str|None = None,
                     password: DelayedStr|str|bool|None = None,
                     apitoken: DelayedStr|str|bool|None = None,
                     force_pk: Any|None = None,
                     modify = False) -> AbstractUser:

    environ_username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    use_environ_params = not username or not environ_username or username == environ_username
    if not username:
        username = environ_username or os.environ.get('USER', os.environ.get('USERNAME', 'admin'))

    if use_environ_params:
        value = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        if value:
            email = value
            
        if is_secret_defined('DJANGO_SUPERUSER_PASSWORD'):
            password = Secret('DJANGO_SUPERUSER_PASSWORD')

    return ensure_user(username, email=email, password=password, apitoken=apitoken, is_staff=True, is_superuser=True, force_pk=force_pk, modify=modify)


def ensure_user(username: str, *,
                email: str|None = None,
                password: DelayedStr|str|bool|None = None,
                apitoken: DelayedStr|str|bool|None = None,
                is_staff: bool|None = None,
                is_superuser: bool|None = None,
                force_pk: Any|None = None,
                modify = False) -> AbstractUser:

    User = get_user_model()

    try:
        user = User.objects.get(username=username)
        change = False
        if force_pk is not None and user.pk != force_pk:
            raise ValueError(f"Invalid PK for {user}: {user.pk} (expected {force_pk})")
    except User.DoesNotExist:
        user = User(username=username)
        change = True
        if force_pk is not None:
            user.pk = force_pk

    if is_staff is not None:
        if user.is_staff != is_staff:
            user.is_staff = is_staff
            change = True

    if is_superuser is not None:
        if user.is_superuser != is_superuser:
            user.is_superuser = is_superuser
            change = True

    if email is not None:
        if not user.email or (modify and email != user.email):
            user.email = email
            change = True

    # Password
    password_to_change = None
    if password is False:
        if modify and user.password:
            password_to_change = ''
    else:
        if password is True:
            password = Secret(f'{user.username.upper()}_PASSWORD', SecretNotFound)
        if not password:
            password = Secret(f'{user.username.upper()}_PASSWORD')
        password = DelayedStr.ensure_value(password)
        if password:
            if not user.password or (modify and not user.check_password(password)):
                password_to_change = password

    if password_to_change is not None:
        if password_to_change == '':
            user.password = ''
        else:
            user.set_password(password_to_change)
        change = True

    # API token
    apitoken_to_change = None
    if apitoken is False:
        if modify:
            from rest_framework.authtoken.models import Token
            if Token.objects.filter(user=user).exists():
                apitoken_to_change = ''
    else:
        if apitoken is True:
            apitoken = Secret(f'{user.username.upper()}_APITOKEN', SecretNotFound)
        if not apitoken:
            apitoken = Secret(f'{user.username.upper()}_APITOKEN')
        apitoken = DelayedStr.ensure_value(apitoken)
        if apitoken:
            from rest_framework.authtoken.models import Token
            current_tokenobj = Token.objects.filter(user=user).first()
            if not current_tokenobj or (modify and current_tokenobj.key != apitoken):
                apitoken_to_change = apitoken
    
    if apitoken_to_change is not None:
        change = True # will be finalized after save of the user (needed to have a primary key)

    # Finalize
    if change:
        _logger.info("%s %s %s", "Update" if user.pk else "Create", "superuser" if is_superuser else "user", user.username)
        user.save()

        if apitoken_to_change is not None:
            from rest_framework.authtoken.models import Token
            if apitoken_to_change == '':
                Token.objects.filter(user=user).delete()
            else:
                Token.objects.update_or_create(user=user, defaults={'key': apitoken_to_change})
    else:
        _logger.debug("No change for user %s", user.username)

    return user

#endregion


#region Management features

def run_management_feature(feature: str):
    """
    Run the class method named with the feature for all models, and run the submodule of the `management` module of all applications.
    """
    def sort_models(model: type[Model]):
        return model.__module__, model.__qualname__
    
    def sort_apps(app: AppConfig):
        return 0 if app.label in {'base', 'core'} else 1, app.label

    def run_for_model(model: type[Model], feature: str):
        try:
            feature_func = getattr(model, feature)
        except AttributeError:
            return
        
        _logger.info(f"Run {feature}() for model {model._meta.app_label}.{model._meta.object_name}")
        feature_func()

    def run_for_app(app: AppConfig, feature: str):
        # Load module
        module_name = f'{app.name}.management.{feature}'
        try:
            module = import_module(module_name)
        except ModuleNotFoundError as err:
            if str(err) in [f"No module named '{module_name}'", f"No module named '{app.name}.management'"]:
                return
            raise
            
        # Run function named with either the feature or as 'main'
        feature_func = getattr(module, feature, None)
        if feature_func is None:
            feature_func = getattr(module, 'main', None)
            if feature_func is None:
                _logger.error(f"Cannot run management.{feature} for model {model._meta.app_label}.{model._meta.object_name}: no function named '{feature}' or 'main'")
                return
            
        _logger.info(f"Run management.{feature}.{feature_func.__name__}() for app {app.name}")
        feature_func()
        
    for app in sorted(apps.get_app_configs(), key=sort_apps):
        for model in sorted(app.get_models(), key=sort_models):
            run_for_model(model, feature)
        run_for_app(app, feature)

#endregion


#region Verify models

def check_field_blanknull(object: Field|type[Model]|Model|str|None = None):
    """
    Warn if a field accepts nulls and not blanks (or the contrary).
    """
    if isinstance(object, (type,Model)):
        for field in object._meta.fields:
            check_field_blanknull(field)
        return
    elif isinstance(object, str):
        app_label = object
        models = apps.get_app_config(app_label).get_models()
        for model in models:
            check_field_blanknull(model)
        return
    elif object is None:
        models = apps.get_models()
        for model in models:
            check_field_blanknull(model)
        return
    elif isinstance(object, Field):
        field = object
    else:
        raise TypeError(f"object: {type(object).__name__}")

    model = field.model
    if model._meta.app_label in ['admin', 'auth', 'contenttypes', 'authtoken', 'authtoken', 'django_celery_results', 'django_celery_beat']:
        return

    if field.blank and not field.null:
        if (field.primary_key
            or field.auto_created
            or isinstance(field, GeneratedField)
            or (isinstance(field, DateField) and (field.auto_now or field.auto_now_add)) or (model == get_user_model() and field.name in ['first_name', 'last_name', 'email'])
        ):
            return
        _logger.warning(f"Field {model._meta.app_label}.{model._meta.object_name}.{field.name} accepts blank but not null")

    elif field.null and not field.blank:
        _logger.warning(f"Field {model._meta.app_label}.{model._meta.object_name}.{field.name} accepts null but not blank")

#endregion


#region Wait for database to be ready

class WaitDbCommand(BaseCommand):
    """
    Usage example, in a file named `myapp/management/commands/waitdb.py`:

    ```
    from zut.django.commands import WaitDbCommand

    class Command(WaitDbCommand):
        pass
    ```
    
    """
    connection_name = 'default'
    default_max_retries = 30

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('--max-retries', type=int, default=None)
        parser.add_argument('--migration', default=None, help="Example: `auth:0001_initial` or `*`")

    def handle(self, *, max_retries: int|None = None, migration: str|tuple[str,str]|Sequence[str|tuple[str,str]]|None = None, **options):
        if max_retries is None:
            max_retries = self.default_max_retries
        current_retries = 0

        from zut.db import get_db

        from django.db import connections

        db = get_db(connections[self.connection_name])
        

        msg = "Waiting for database"
        if migration:
            msg += f" (migration \"{migration}\")"
        self.stdout.write(msg, ending='')
        self.stdout.flush()
        
        while not db.is_available(migrations=migration):
            if not current_retries and max_retries > 0:
                self.stdout.write("\nRetrying... ", ending='')
                self.stdout.flush()

            if current_retries >= max_retries:
                self.stdout.write(" " + self.style.ERROR("NOT AVAILABLE"))
                exit(1)
            
            sleep(1)
            self.stdout.write(".", ending='')
            self.stdout.flush()
            current_retries += 1

        self.stdout.write(" " + self.style.SUCCESS("OK"))

#endregion
