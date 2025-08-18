from __future__ import annotations

import logging
from datetime import date
from typing import TYPE_CHECKING, Any, Callable, Generic, Literal, NamedTuple, Sequence, TypeVar, Union, overload

from zut.django.middleware import ThreadLocalMiddleware
from zut.tz import now_aware

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.core.exceptions import FieldDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import DateTimeField, Field, Model, TextChoices, signals
from django.db.models.expressions import DatabaseDefault  # pyright: ignore[reportAttributeAccessIssue]

if TYPE_CHECKING:
    ModelTypeHint = Model
    """ A type hint which avoid a subclass to be actually considered as a model by Django. """
else:
    ModelTypeHint = object

T_Model = TypeVar('T_Model', bound=Model)

_logger = logging.getLogger(__name__)


class HistoryStatus(TextChoices):
    CREATED = '+'
    CHANGED = '~'
    UPTODATE = ('=', "Up-to-date")
    DELETED = '-'


@overload
def historize(*,
        only_changes: bool = True,
        ignore: str|Sequence[str] = [],
        transient: str|Sequence[str] = [],
        explicit: str|Sequence[str] = [],
        extra: str|Sequence[str] = ['extra']
        ) -> Callable[[type[T_Model]], type[T_Model]]:
    """
    This decorator creates a historical model associated to the given model and attach the adequate history manager to it.

    :param only_changes: If true, add a history only if the data changed or was deleted.
    :param ignore: Ignore attribute(s) when building snapshots. The history manager will behave as if these attributes did not exist at all.
    :param transient: Changes to these attribute(s) will not be counted as changes.
    :param explicit: These attribute(s) will have a dedicated field in the history model to follow the changes.
    :param extra: These field(s) are considered by the history manager as JSON objects for which the comparison must be done on all keys of the JSON object.
    """
    ...

@overload
def historize(model: type[T_Model], *,
        only_changes: bool = True,
        ignore: str|Sequence[str] = [],
        transient: str|Sequence[str] = [],
        explicit: str|Sequence[str] = [],
        extra: str|Sequence[str] = ['extra']
        ) -> type[T_Model]:
    """
    This decorator creates a historical model associated to the given model and attach the adequate history manager to it.
    """
    ...

def historize(model: type[T_Model]|None = None, **options): # type: ignore
    """
    This decorator creates a historical model associated to the given model and attach the adequate history manager to it.
    """
    if model is not None: # decorator used without arguments: `@historize`
        register_history(model, **options)
        return model
    
    else: # decorator used with arguments, for example `@historize(transient='freespace')` or `@itemclass()`            
        def decorator(model):
            register_history(model, **options)
            return model

        return decorator


def register_history(model: type[Model], **options):
    _logger.debug("Register history model for %s", model)
    recorder = HistoryRecorder(model, **options)
    setattr(model, 'history_model', recorder.create_history_model())

    # We need strong references otherwise the HistoryRecorder object would be discarded
    signals.post_init.connect(recorder.post_init, sender=model, weak=False)
    signals.post_save.connect(recorder.post_save, sender=model, weak=False)
    signals.post_delete.connect(recorder.post_delete, sender=model, weak=False)
    

BuildPrevResult = NamedTuple('BuildPrevResult', [('prev', dict[str,Any]), ('nontrasient_changes', list[str])])


class HistoryRecorder:
    def __init__(self, model: type[Model], *,
        only_changes: bool = True,
        ignore: str|Sequence[str] = [],
        transient: str|Sequence[str] = [],
        explicit: str|Sequence[str] = [],
        extra: str|Sequence[str] = ['extra'],
        related_name: str = 'history_set',
        date_indexing: Literal[True,False,'composite'] = True,
        use_base_model_db: bool = False,
    ):

        self.model = model
        self.only_changes = only_changes

        if isinstance(ignore, str):
            ignore = [ignore]
        self.ignore_attnames: set[str] = set()
        for name in ignore:
            field = self.model._meta.get_field(name)
            self.ignore_attnames.add(field.attname)

        if isinstance(explicit, str):
            explicit = [explicit]
        self.explicit_fields: list[Field] = []
        self.explicit_attnames: set[str] = set()
        for name in explicit:
            field = self.model._meta.get_field(name)
            self.explicit_fields.append(field)
            self.explicit_attnames.add(field.attname)

        if isinstance(transient, str):
            transient = [transient]
        self.transient_fields: list[Field] = []
        self.transient_attnames: set[str] = set()
        for name in transient:
            field = self.model._meta.get_field(name)
            self.transient_fields.append(field)
            self.transient_attnames.add(field.attname)

        if isinstance(extra, str):
            extra = [extra]
        self.extra_attnames: set[str] = set()
        for name in extra:
            try:
                field = self.model._meta.get_field(name)
            except FieldDoesNotExist:
                if name == 'extra': # default
                    continue
                else:
                    raise
            self.extra_attnames.add(field.attname)

        self.related_name = related_name
        self.date_indexing = date_indexing
        self.use_base_model_db = use_base_model_db

        self.history_prev_at_attname: str|None = None
        for field in self.model._meta.fields:
            if isinstance(field, DateTimeField) and field.auto_now:
                self.history_prev_at_attname = field.attname
                break


    def post_init(self, instance: HistorisedModel, **kwargs):
        if getattr(settings, "HISTORY_DISABLED", False):
            return
        instance._history_snapshot = self.build_snapshot(instance)
        instance.last_history_status = None


    def post_save(self, instance: HistorisedModel, created: bool, using=None, **kwargs):
        if getattr(settings, "HISTORY_DISABLED", False):
            return
        self.create_historical_record(instance, created, using=using)


    def post_delete(self, instance: HistorisedModel, using=None, **kwargs):
        if getattr(settings, "HISTORY_DISABLED", False):
            return
        self.create_historical_record(instance, 'DELETED', using=using)


    def create_historical_record(self, instance: HistorisedModel, created: bool|Literal['DELETED'], using=None):
        history_prev_at: date|None = None
        history_note: str|None = getattr(instance, 'history_note', None)
        prev: dict|None = None
        prev_explicit = {}

        if created is True:
            instance.last_history_status = HistoryStatus.CREATED
            if self.only_changes:
                return

        else:
            if self.history_prev_at_attname:
                history_prev_at = instance._history_snapshot.get(self.history_prev_at_attname)
            
            if created == 'DELETED':
                instance.last_history_status = HistoryStatus.DELETED
                # Copy entire history snapshot
                prev_explicit, _ = self.build_prev_explicit(instance._history_snapshot)
                prev = {}
                for attname, value in instance._history_snapshot.items():
                    if self.model._meta.pk is None or attname == self.model._meta.pk.attname or attname == self.history_prev_at_attname or attname in self.explicit_attnames:
                        continue
                    if value is not None:
                        prev[attname] = value

            else: # UPDATED (CHANGED or NOTCHANGED)
                # Keep only previous values of changes
                current_snapshot = self.build_snapshot(instance)
                if self.explicit_fields:
                    prev_explicit, prev_explicit_nontransient_changes = self.build_prev_explicit(instance._history_snapshot, current_snapshot)
                else:
                    prev_explicit_nontransient_changes = []

                prev, prev_nontransient_changes = self.build_prev(instance._history_snapshot, current_snapshot)
                if not prev_explicit_nontransient_changes and not prev_nontransient_changes:
                    instance.last_history_status = HistoryStatus.UPTODATE
                    if self.only_changes:
                        return
                else:
                    instance.last_history_status = HistoryStatus.CHANGED

        history_instance = instance.history_model(
            history_object=instance,
            history_status=instance.last_history_status,
            history_at=now_aware(),
            history_user=self.get_history_user(instance),
            history_note=history_note,
            history_prev_at=history_prev_at,
            prev=None if not prev else prev,
            **prev_explicit,
        )

        history_instance.save(using=using if self.use_base_model_db else None)


    def build_snapshot(self, instance: Model):
        snapshot = {}

        field: Field
        for field in self.model._meta.fields:
            if field.attname in self.ignore_attnames:
                continue
            value = getattr(instance, field.attname)
            if value is not None:
                if isinstance(value, DatabaseDefault):
                    value = None
                else:
                    value = field.to_python(value)
            snapshot[field.attname] = value

        return snapshot


    def build_prev_explicit(self, history_snapshot: dict, current_snapshot: dict|None = None) -> BuildPrevResult:
        prev_explicit = {}
        list_of_nontransient_changes = []

        for field in self.explicit_fields:
            prev_value = history_snapshot.get(field.attname)
            prev_explicit[f'prev_{field.attname}'] = prev_value

            if current_snapshot is not None and not field.attname in self.transient_attnames:
                current_value = current_snapshot.get(field.attname)
                if current_value != prev_value:
                    list_of_nontransient_changes.append(field.attname)

        return BuildPrevResult(prev_explicit, list_of_nontransient_changes)
    

    def build_prev(self, history_snapshot: dict, current_snapshot: dict) -> BuildPrevResult:
        prev = {}
        list_of_nontransient_changes = []

        def is_external_attname(attname: str):
            return attname in self.explicit_attnames or attname == self.history_prev_at_attname

        no_change = object()
        for attname, value in history_snapshot.items():
            if is_external_attname(attname):
                continue

            new_value = no_change
            if attname in current_snapshot:
                if attname in self.extra_attnames and isinstance(current_snapshot[attname], dict) and isinstance(value, dict):
                    extra_prev = self.build_extra_prev(value, current_snapshot[attname])
                    if extra_prev:
                        new_value = extra_prev
                elif current_snapshot[attname] != value:
                    new_value = value
            else:
                new_value = value

            if new_value is not no_change:
                prev[attname] = new_value
                if not attname in self.transient_attnames:
                    list_of_nontransient_changes.append(attname)

        for attname, value in current_snapshot.items():
            if is_external_attname(attname):
                continue

            if not attname in history_snapshot:
                prev[attname] = None
                if not attname in self.transient_attnames:
                    list_of_nontransient_changes.append(attname)

        return BuildPrevResult(prev, list_of_nontransient_changes)


    def build_extra_prev(self, history_extra: dict, current_extra: dict):
        extra_prev = {}

        for key, value in history_extra.items():
            if key in current_extra:
                if current_extra[key] != value:
                    extra_prev[key] = value
            else:
                extra_prev[key] = value

        for key, value in current_extra.items():
            if not key in history_extra:
                extra_prev[key] = None

        return extra_prev


    def get_history_user(self, instance: HistorisedModel):
        """
        Get the modifying user from instance or middleware.
        """
        try:
            return instance.history_user
        except AttributeError:
            request = ThreadLocalMiddleware.get_request()
            if request.user.is_authenticated:
                instance.history_user = request.user if not isinstance(request.user, AnonymousUser) else None
                return instance.history_user
            else:
                return None


    def create_history_model(self):
        """
        Creates a historical model to associate with the model provided.
        """
        name = f'{self.model._meta.object_name}_History'
        bases = (HistoryModel, Model)
        attrs = {
            '__module__': self.model.__module__,
            'Meta': type('Meta', (), self.get_meta_options()),
            # Fields
            'history_id': models.BigAutoField(primary_key=True),
            'history_object': models.ForeignKey(self.model, on_delete=models.DO_NOTHING, related_name=self.related_name, db_constraint=False),
            'history_status': models.CharField(max_length=1, choices=HistoryStatus.choices),
            'history_note': models.CharField(max_length=1000, blank=True, null=True),
            'history_at': models.DateTimeField(db_index=self.date_indexing is True),
            'history_user': models.ForeignKey(get_user_model(), blank=True, null=True, on_delete=models.SET_NULL),
            'history_prev_at': models.DateTimeField(db_index=self.date_indexing is True, blank=True, null=True),
            'prev': models.JSONField(blank=True, null=True, encoder=DjangoJSONEncoder),
        }

        for field in self.explicit_fields:
            prev_field = self.get_prev_field(field)
            attrs[f'prev_{field.attname}'] = prev_field

        history_model = type(name, bases, attrs)
        return history_model
    

    def get_prev_field(self, field: Field):
        """
        Creates a prev field based on the model's original field.
        """
        attrs = {
            'null': True,
            'blank': True,
            'editable': False,
        }

        for key, value in field.__dict__.items():
            if key.startswith('_') or key in attrs:
                continue
            if key in {'primary_key', 'name', 'attname', 'model', 'default', 'db_default', 'creation_counter', 'auto_created',
                       'concrete', 'hidden', 'is_relation', 'serialize', 'help_text', 'remote_field', 'verbose_name',
                       'column', 'db_column', 'db_index', 'db_comment', 'db_collation', 'unique', 'unique_for_date', 'unique_for_month', 'unique_for_year',
                       'auto_now', 'auto_now_add'}:
                continue
            attrs[key] = value
        
        prev_field_cls: type
        if isinstance(field, models.BigAutoField):
            prev_field_cls = models.BigIntegerField
        elif isinstance(field, models.AutoField):
            prev_field_cls = models.IntegerField
        elif isinstance(field, models.FileField):
            prev_field_cls = models.CharField # Don't copy file, just path.
        else:
            prev_field_cls = field.__class__

        prev_field = prev_field_cls(**attrs)
        return prev_field


    def get_meta_options(self):
        options = {
            'app_label': self.model._meta.app_label,
            'ordering': ('-history_at', '-history_id'),
            'get_latest_by': ('history_at', 'history_id'),
            'verbose_name': f'{self.model._meta.verbose_name} (history)',
            'verbose_name_plural': f'{self.model._meta.verbose_name_plural} (history)',
        }

        if self.date_indexing:
            options['indexes'] = (
                models.Index(fields=('history_at', 'history_object_id')),
            )

        return options


class HistorisedModel(ModelTypeHint):
    _history_snapshot: dict
    history_model: type[HistoryModel]
    last_history_status: HistoryStatus|None

    history_user: AbstractUser|None
    """ User making the change. Can be set manually before saving, or will be set automatically if ThreadLocalMiddleware is included in Django middleware settings. """

    history_note: str|None
    """ Custom note and/or list of additional fields or data changed. """


class HistoryModel(ModelTypeHint):
    history_id: models.BigAutoField
    history_object: models.ForeignKey
    history_status: models.CharField
    history_note: models.CharField
    history_at: models.DateTimeField
    history_user: models.ForeignKey
    history_prev_at: models.DateTimeField
    prev: models.JSONField
