"""
Utilities for models.
"""
from __future__ import annotations

import re
from contextlib import contextmanager

from django.apps import apps
from django.db.models import DateField, Model
from django.urls import reverse


def admin_url(model: type[Model]|str|Model):
    """
    Get admin URL of the given model.
    
    Reference: https://docs.djangoproject.com/en/5.1/ref/contrib/admin/#reversing-admin-urls
    """
    pk = None
    if isinstance(model, (type,Model)):
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        if isinstance(model, Model):
            pk = model.pk
    else:
        m = re.match(r'^([a-z0-9_]+)[\._]([a-z0-9_]+)$', model, re.IGNORECASE)
        if m:
            app_label = m[1]
            model_name = m[2]
        else:
            raise ValueError(f"Invalid model type string: {model}")

    prefix = 'admin:%s_%s' % (app_label, model_name)
    if pk is None:
        return reverse(f'{prefix}_changelist')
    else:
        return reverse(f'{prefix}_change', args=[pk])


@contextmanager
def disable_auto_now(*models: type[Model]):
    """
    Temporarily disable `auto_now` and `auto_now_add` for the fields of the given model(s).

    See: https://stackoverflow.com/a/67356850
    """
    if not models:
        _models = apps.get_models()
    else:
        _models = models
    
    fields: list[DateField] = []
    for model in _models:
        if isinstance(model, type) and issubclass(model, Model):
            for field in model._meta.get_fields():
                if isinstance(field, DateField):
                    fields.append(field)
        else:
            raise TypeError(f"Model: {model}")
    
    fields_state: dict[DateField,dict[str,bool]] = {}
    for field in fields:
        fields_state[field] = {'auto_now': field.auto_now, 'auto_now_add': field.auto_now_add}

    for field in fields_state:
        field.auto_now = False
        field.auto_now_add = False
    try:
        yield
    finally:
        for field, state in fields_state.items():
            field.auto_now = state['auto_now']
            field.auto_now_add = state['auto_now_add']
