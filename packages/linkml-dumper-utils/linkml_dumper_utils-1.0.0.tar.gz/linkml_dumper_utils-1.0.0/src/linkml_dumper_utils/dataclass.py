import json
import keyword
import sys
import types
from dataclasses import dataclass, is_dataclass, asdict
from pathlib import Path
from typing import Any, Callable, ClassVar

import rdflib
from linkml_runtime import SchemaView
from linkml_runtime.dumpers import rdflib_dumper

from linkml_dumper_utils.common import make_jsonld_mixin, make_rdflib_mixin


def _is_dataclass_instance(obj: Any) -> bool:
    # technically there is also a private method in the official dataclasses module
    return is_dataclass(obj) and not isinstance(obj, type)


# @dataclass
class LinkMLDataclassMixin: pass

class LinkMLDataclassMixinRdflibBase(LinkMLDataclassMixin):
    _schema_cache: ClassVar[dict] = {}
    class_name: ClassVar[str] = ''

DataclassRdflibMixin = make_rdflib_mixin(LinkMLDataclassMixinRdflibBase)

class LinkMLDataclassMixinJsonldBase(LinkMLDataclassMixin):
    _context_cache: ClassVar[dict] = {}

DataclassJsonldMixin = make_jsonld_mixin(LinkMLDataclassMixinJsonldBase)


def as_json_string(obj) -> str:
    if not _is_dataclass_instance(obj):
        raise TypeError('as_json_string() should be called on dataclass instances')
    return json.dumps(asdict(obj))


def as_json_ld_string(obj: DataclassJsonldMixin) -> str:
    if not _is_dataclass_instance(obj):
        raise TypeError('as_json_ld_string() should be called on dataclass instances')
    if not isinstance(obj, DataclassJsonldMixin):
        raise TypeError('as_json_ld_string() should be called on JsonldMixin instances')
    return json.dumps(as_json_ld(obj))


def as_json_ld(obj, **kwargs) -> dict:
    if not _is_dataclass_instance(obj):
        raise TypeError('as_json_ld() should be called on dataclass instances')
    if not isinstance(obj, DataclassJsonldMixin):
        raise TypeError('as_json_ld() should be called on JsonldMixin instances')

    dump = asdict(obj, **kwargs)
    dump['@context'] = obj._context_cache[obj.__class__]
    dump['@type'] = obj.__class__.__name__
    return dump


def as_rdf_string(obj, **kwargs) -> str:
    return rdflib_dumper.dumps(obj, schemaview=obj._schema_cache[obj.__class__], **kwargs)


def as_rdflib_graph(obj, **kwargs) -> rdflib.Graph:
    return rdflib_dumper.as_rdf_graph(obj, schemaview=obj._schema_cache[obj.__class__], **kwargs)


def make_custom_dataclass(cls_name, fields, *, bases=(), namespace=None, init=True,
                   repr=True, eq=True, order=False, unsafe_hash=False,
                   frozen=False, match_args=True, kw_only=False, slots=False,
                   weakref_slot=False, module=None, cls_kwargs=None):
    if cls_kwargs is None:
        cls_kwargs = {}
    if namespace is None:
        namespace = {}

    # While we're looking through the field names, validate that they
    # are identifiers, are not keywords, and not duplicates.
    seen = set()
    annotations = {}
    defaults = {}
    for item in fields:
        if isinstance(item, str):
            name = item
            tp = 'typing.Any'
        elif len(item) == 2:
            name, tp, = item
        elif len(item) == 3:
            name, tp, spec = item
            defaults[name] = spec
        else:
            raise TypeError(f'Invalid field: {item!r}')

        if not isinstance(name, str) or not name.isidentifier():
            raise TypeError(f'Field names must be valid identifiers: {name!r}')
        if keyword.iskeyword(name):
            raise TypeError(f'Field names must not be keywords: {name!r}')
        if name in seen:
            raise TypeError(f'Field name duplicated: {name!r}')

        seen.add(name)
        annotations[name] = tp

    # Update 'ns' with the user-supplied namespace plus our calculated values.
    def exec_body_callback(ns):
        ns.update(namespace)
        ns.update(defaults)
        ns['__annotations__'] = annotations

    # We use `types.new_class()` instead of simply `type()` to allow dynamic creation
    # of generic dataclasses.
    cls = types.new_class(cls_name, bases, cls_kwargs, exec_body_callback)

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the dataclass is created.
    if module is None:
        try:
            module = sys._getframemodulename(1) or '__main__'
        except AttributeError:
            try:
                module = sys._getframe(1).f_globals.get('__name__', '__main__')
            except (AttributeError, ValueError):
                pass
    if module is not None:
        cls.__module__ = module

    # Apply the normal decorator.
    return dataclass(cls, init=init, repr=repr, eq=eq, order=order,
                     unsafe_hash=unsafe_hash, frozen=frozen,
                     match_args=match_args, kw_only=kw_only, slots=slots,
                     weakref_slot=weakref_slot)


def dataclass_jsonld_mixin(context_file_path: Path = None, context_string: str = None, context: dict = None) -> Callable[[type], type]:
    def decorator(base: type) -> type:
        kwargs = {
            'context_file_path': context_file_path,
            'context_string': context_string,
            'context': context
        }
        mixin = make_custom_dataclass(f'{base.__name__}JsonldMixin', fields=[], bases=(DataclassJsonldMixin,), cls_kwargs=kwargs)
        return make_custom_dataclass(f'{base.__name__}', fields=[], bases=(mixin, base))
    return decorator


def dataclass_rdflib_mixin(schema_file_path: Path = None, schema_string: str = None, schema_view: SchemaView = None) -> Callable[[type], type]:
    def decorator(base: type) -> type:
        kwargs = {
            'schema_file_path': schema_file_path,
            'schema_string': schema_string,
            'schema_view': schema_view
        }
        mixin = make_custom_dataclass(f'{base.__name__}RdflibMixin', fields=[], bases=(DataclassRdflibMixin,), cls_kwargs=kwargs)
        return make_custom_dataclass(f'{base.__name__}', fields=[], bases=(mixin, base))
    return decorator

