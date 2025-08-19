import json
from pathlib import Path
from typing import ClassVar, Any, Callable

import rdflib
from linkml_runtime import SchemaView
from linkml_runtime.dumpers import rdflib_dumper
from pydantic import BaseModel, create_model

from linkml_dumper_utils.common import make_jsonld_mixin, make_rdflib_mixin


# class LinkMLPydanticMixin(BaseModel): pass
class LinkMLPydanticMixin: pass

class LinkMLPydanticMixinRdflibBase(LinkMLPydanticMixin):
    _schema_cache: ClassVar[dict] = {}
    class_name: ClassVar[str] = ''

    def model_dump_rdf_string(self, **kwargs) -> str:
        return rdflib_dumper.dumps(self, schemaview=self._schema_cache[self.__class__], **kwargs)

    def model_dump_rdflib_graph(self, **kwargs) -> rdflib.Graph:
        return rdflib_dumper.as_rdf_graph(self, schemaview=self._schema_cache[self.__class__], **kwargs)

PydanticRdflibMixin = make_rdflib_mixin(LinkMLPydanticMixinRdflibBase)

def pydantic_rdflib_mixin(schema_file_path: Path = None, schema_string: str = None, schema_view: SchemaView = None) -> Callable[[type[BaseModel]], type[BaseModel]]:
    def decorator(base: type[BaseModel]) -> type[BaseModel]:
        kwargs = {
            'schema_file_path': schema_file_path,
            'schema_string': schema_string,
            'schema_view': schema_view
        }
        mixin = type(f'{base.__name__}RdflibMixin', (PydanticRdflibMixin,), {}, **kwargs)
        # mixin = create_model(f'{base.__name__}RdflibMixin', __base__=PydanticRdflibMixin, __cls_kwargs__=kwargs)
        return create_model(f'{base.__name__}', __base__=(mixin, base))
    return decorator


class LinkMLPydanticMixinJsonldBase(LinkMLPydanticMixin):
    _context_cache: ClassVar[dict] = {}

    def model_dump_jsonld_string(self, **kwargs) -> str:
        return json.dumps(self.model_dump_jsonld(**kwargs))

    def model_dump_jsonld(self, **kwargs) -> dict[str, Any]:
        # dump = super().model_dump(**kwargs)
        dump = self.model_dump(**kwargs)
        dump['@context'] = self._context_cache[self.__class__]
        return dump

PydanticJsonldMixin = make_jsonld_mixin(LinkMLPydanticMixinJsonldBase)

def pydantic_jsonld_mixin(context_file_path: Path = None, context_string: str = None, context: dict = None) -> Callable[[type[BaseModel]], type[BaseModel]]:
    def decorator(base: type[BaseModel]) -> type[BaseModel]:
        kwargs = {
            'context_file_path': context_file_path,
            'context_string': context_string,
            'context': context
        }
        mixin = type(f'{base.__name__}JsonldMixin', (PydanticJsonldMixin,), {}, **kwargs)
        # mixin = create_model(f'{base.__name__}JsonldMixin', __base__=PydanticJsonldMixin, __cls_kwargs__=kwargs)
        # JsonldMixin.__pydantic_init_subclass__(mixin, context_file_path=context_file_path, context_string=context_string)
        return create_model(f'{base.__name__}', __base__=(mixin, base))
    return decorator
