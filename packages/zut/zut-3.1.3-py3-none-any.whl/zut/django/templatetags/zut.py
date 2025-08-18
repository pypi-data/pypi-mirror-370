from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from django import template
from django.apps import apps
from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS
from django.forms import Form, widgets
from django.forms.boundfield import BoundField
from django.template import RequestContext
from django.templatetags.static import static
from django.utils.html import escape
from django.utils.safestring import mark_safe

try:
    from django_vite.core.asset_loader import DjangoViteAssetLoader
except ModuleNotFoundError:
    DjangoViteAssetLoader = None
    
from ..models import admin_url as _admin_url

register = template.Library()

_logger = logging.getLogger(__name__)


#region General

@register.simple_tag
def admin_url(model):
    return _admin_url(model)


@register.filter
def prefix_unless_empty(value: str, prefix: str):
    value = value.strip()
    if not value:
        return value
    else:
        return f"{prefix}{value}"


@register.filter
def suffix_unless_empty(value: str, suffix: str):
    value = value.strip()
    if not value:
        return value
    else:
        return f"{value}{suffix}"

#endregion


#region Lib script and style HTML tags

@register.simple_tag
def style_lib(package, file, version=None, integrity=None):
    """
    Usage example in Django base template:

        {% load static base %}
        ...
        <head>
        ...
        {% style_lib  'bootstrap' 'dist/css/bootstrap.min.css' '5.2.0' 'sha256-7ZWbZUAi97rkirk4DcEp4GWDPkWpRMcNaEyXGsNXjLg=' %}
        ...
        </head>
    """
    if file and version and re.match(r'^\d+', file):
        # invert
        arg2 = file
        file = version
        version = arg2

    url = _get_lib_url(package, file, version)

    if not version and not url in _missing_version:
        _logger.warning(f"Missing version for style_lib: {url}")
        _missing_version.add(url)
        
    html = f"<link rel=\"stylesheet\" href=\"{url}\""
    
    if integrity:
        html += f" integrity=\"{integrity}\" crossorigin=\"anonymous\""
    elif not url in _missing_integrity:
        _logger.warning(f"Missing integrity hash for style_lib: {url}")
        _missing_integrity.add(url)

    html += f" />"
    return mark_safe(html)


@register.simple_tag
def script_lib(package, file, version=None, integrity=None, *, no_defer = False):
    """
    Usage example in Django base template:

        {% load static base %}
        ...
        <head>
        ...
        {% script_lib 'bootstrap' 'dist/js/bootstrap.bundle.min.js' '5.2.0' 'sha256-wMCQIK229gKxbUg3QWa544ypI4OoFlC2qQl8Q8xD8x8=' %}
        ...
        </head>
    """
    if file and version and re.match(r'^\d+', file):
        # invert
        arg2 = file
        file = version
        version = arg2
    
    url = _get_lib_url(package, file, version)
    
    if not version and not url in _missing_version:
        _logger.warning(f"Missing version for script_lib: {url}")
        _missing_version.add(url)

    html = f"<script"
    if not no_defer:
        html += " defer"
    html += f" src=\"{url}\""
    
    if integrity:
        html += f" integrity=\"{integrity}\" crossorigin=\"anonymous\""
    elif not url in _missing_integrity:
        _logger.warning(f"Missing integrity hash for script_lib: {url}")
        _missing_integrity.add(url)

    html += f"></script>"
    return mark_safe(html)

# avoid logging warnings for every request
_missing_version: set[str] = set()
_missing_integrity: set[str] = set()

def _get_lib_url(package, file, version=None, prefix=None):
    if getattr(settings, 'LOCAL_STATIC_LIB', False):
        return static(f"lib/{package}/{file}")
    else:
        if version:
            return f"https://cdn.jsdelivr.net/npm/{package}@{version}/{file}"
        else:
            return f"https://cdn.jsdelivr.net/npm/{package}/{file}"
        
#endregion


#region Page script tags

@register.simple_tag(takes_context=True)
def page_script(context: RequestContext, *, no_defer = False):
    if context.get('csrf_token_added_to_html'):
        html = ''
    else:
        csrf_token = context.get('csrf_token')
        html = f'<input id="csrfmiddlewaretoken" type="hidden" value="{csrf_token}" />' if csrf_token != 'NOTPROVIDED' else ''
        context['csrf_token_added_to_html'] = True

    r = context.request.resolver_match
    if not r:
        raise ValueError("Cannot find resolver match")
    asset_url = app_asset_url(f"{r.namespace}/{r.url_name}.ts")
    
    html += f'<script'
    if not no_defer:
        html += " defer"
    html += f' type="module" src="{asset_url}"></script>'
    return mark_safe(html)

#endregion


#region Asset URLs

@register.simple_tag
def app_asset_url(path: str):
    if DjangoViteAssetLoader:
        # We use vite
        m = re.match(r'^(?P<app_label>[^/]+)/.+$', path)
        if not m:
            raise ValueError(f"Not an app asset: {path}")
        app_path = Path(apps.get_app_config(m['app_label']).path)
        asset_path = os.path.relpath(f"{app_path}/assets/{path}", settings.BASE_DIR)
        return DjangoViteAssetLoader.instance().generate_vite_asset_url(asset_path)
    else:
        # We do not use vite
        return static(path)

#endregion        


#region Forms

@register.filter
def field_attrs(field: BoundField, attrs: str):
    # See original idea: https://stackoverflow.com/a/69196141
    actual_attrs = dict(field.field.widget.attrs)
    css_classes = actual_attrs['class'].split(' ') if 'class' in actual_attrs else []

    for attr in attrs.split(','):
        if ':' not in attr:
            for css_class in attr.split(' '):
                if css_class not in css_classes:
                    css_classes.append(css_class)
        else:
            key, val = attr.split(':')
            actual_attrs[key] = val
    
    if css_classes:
        actual_attrs['class'] = ' '.join(css_classes)
    return field.as_widget(attrs=actual_attrs) # type: ignore


@register.filter
def field_horizontal(field: BoundField, label_col = 4):    
    widget = field.field.widget
    if isinstance(widget, (widgets.CheckboxInput, widgets.RadioSelect)):
        attrs = 'form-check-input'
    elif isinstance(widget, (widgets.Select, widgets.SelectMultiple)):
        attrs = 'form-select'
    else:
        attrs = 'form-control'

    if field.errors:
        attrs += ' is-invalid'
    
    html = f'''<div class="row mb-{label_col}">
        <label for="{field.auto_id}" class="col-sm-4 col-form-label">{field.label}</label>
        <div class="col-sm-{12 - label_col}">'''
    
    html += field_attrs(field, attrs)

    if field.errors:
        html += '<div class="invalid-feedback">'
        for error in field.errors:
            html += f'<div>{escape(error)}</div>'
        html += '</div>'
    
    html += '''</div>
    </div>'''
    return mark_safe(html)


@register.filter
def form_horizontal(form: Form, label_col = 4):
    html = ''

    if form.errors:
        html += '<div class="alert alert-danger" role="alert">'
        for error in form.non_field_errors():
            html += f'<div>{escape(error)}</div>'
        fields_with_errors = [f"<strong>{name}</strong>" for name in form.errors if name != NON_FIELD_ERRORS]
        if fields_with_errors:
            html += f'<div>Invalid field{"s" if len(fields_with_errors) > 1 else ""}: {", ".join(fields_with_errors)}.</div>'
        html += '</div>'

    for field in form:
        html += field_horizontal(field, label_col=label_col)

    return mark_safe(html)

#endregion
