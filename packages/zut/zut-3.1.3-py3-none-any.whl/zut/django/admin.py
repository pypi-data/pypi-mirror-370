from __future__ import annotations

from import_export.admin import ImportExportMixin

from django.contrib.gis.admin import GISModelAdmin, StackedInline, TabularInline, display, register
from django.db.models import Field, Model
from django.forms import ModelForm
from django.http import HttpRequest


class ModelAdmin(ImportExportMixin, GISModelAdmin): # type: ignore
    gis_widget_kwargs = {'attrs': {'default_lat': 43.30, 'default_lon': 5.37}}

    def save_model(self, request: HttpRequest, obj: Model, form: ModelForm, change: bool):
        field: Field
        for field in obj._meta.fields:
            # Transform blank values to null values if the field accepts null values
            if field.null:
                value = getattr(obj, field.attname, None)
                if value == '':
                    setattr(obj, field.attname, None)

            # Set default inserted_by and updated_by value
            if not field.editable:
                if change: # UPDATE
                    if field.name == 'updated_by':
                        setattr(obj, field.attname, request.user.pk)
                else: # INSERT
                    if field.name == 'inserted_by' or field.name == 'updated_by':
                        setattr(obj, field.attname, request.user.pk)
        
        super().save_model(request, obj, form, change)


__all__ = ('ModelAdmin',
           # Shortcuts
           'TabularInline', 'StackedInline', 'display', 'register',)
