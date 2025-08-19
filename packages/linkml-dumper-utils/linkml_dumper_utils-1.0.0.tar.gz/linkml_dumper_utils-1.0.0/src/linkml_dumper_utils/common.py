import json
from pathlib import Path

from linkml_runtime import SchemaView


def _load_context_from_file(context_file_path: Path) -> dict:
    with open(context_file_path, 'rb') as stream:
        return json.load(stream)

def make_jsonld_mixin(dataclass_or_pydantic_base: type):

    class JsonldMixin(dataclass_or_pydantic_base):
        @classmethod
        def __init_subclass__(cls, context_file_path: Path = None, context_string: str = None, context: dict = None):
            super().__init_subclass__()
            if JsonldMixin in cls.__bases__:  # direct child
                args = [context_file_path, context_string, context]
                arg_count = sum(x is not None for x in args)

                if arg_count != 1:
                    raise RuntimeError(
                        'You must pass exactly one of the context_file_path, context_string, or the context argument')

                if context_file_path is not None:
                    context = _load_context_from_file(context_file_path)
                elif context_string is not None:
                    context = json.loads(context_string)

                dataclass_or_pydantic_base._context_cache[cls] = context
            else:  # grandchild
                for base_class in cls.__mro__:
                    if base_class in JsonldMixin._context_cache:
                        JsonldMixin._context_cache[cls] = JsonldMixin._context_cache[base_class]
    return JsonldMixin

def make_rdflib_mixin(dataclass_or_pydantic_base: type):
    class RdflibMixin(dataclass_or_pydantic_base):
        @classmethod
        def __init_subclass__(cls, schema_file_path: Path = None, schema_string: str = None,
                              schema_view: SchemaView = None):
            super().__init_subclass__()
            cls.class_name = cls.__name__
            if RdflibMixin in cls.__bases__:  # direct child
                args = [schema_file_path, schema_string, schema_view]
                arg_count = sum(x is not None for x in args)

                if arg_count != 1:
                    raise RuntimeError(
                        'You must pass exactly one of the schema_file_path, schema_string, or the schema_view argument')

                if schema_file_path is not None:
                    schema_view = SchemaView(schema_file_path)
                elif schema_string is not None:
                    schema_view = SchemaView(schema_string)

                RdflibMixin._schema_cache[cls] = schema_view
            else:  # grandchild
                for base_class in cls.__mro__:
                    if base_class in RdflibMixin._schema_cache:
                        RdflibMixin._schema_cache[cls] = RdflibMixin._schema_cache[base_class]
    return RdflibMixin