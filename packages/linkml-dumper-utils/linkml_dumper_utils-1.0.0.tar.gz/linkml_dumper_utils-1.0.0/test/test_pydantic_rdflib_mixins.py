from pydantic import BaseModel
import pytest

from linkml_dumper_utils.pydantic import PydanticRdflibMixin, pydantic_rdflib_mixin


@pytest.fixture
def simple_schema():
    return """
id: http://troll.org/
name: troll
prefixes:
    troll: http://troll.org/
default_prefix: troll
imports:
    - linkml:types
classes:
    Simple:
        class_uri: troll:Simple
        attributes:
            x:
                range: integer
"""


def test_linkml_rdflib_mixin(simple_schema):
    @pydantic_rdflib_mixin(schema_string=simple_schema)
    class Simple(BaseModel):
        x: int

    @pydantic_rdflib_mixin(schema_string=simple_schema.replace(' x:', ' y:').replace('Simple:', 'Simple2:'))
    class Simple2(BaseModel):
        y: int

    s = Simple(x=42)
    s2 = Simple2(y=21)

    rdf_string = s.model_dump_rdf_string()
    rdf_string2 = s2.model_dump_rdf_string()

    assert '[] a troll:Simple' in rdf_string
    assert 'troll:x 42' in rdf_string


def test_pydantic_rdflib_mixin_with_inheritance(simple_schema):
    class Simple(BaseModel, PydanticRdflibMixin, schema_string=simple_schema):
        x: int

    s = Simple(x=42)
    rdf_string = s.model_dump_rdf_string()

    assert '[] a troll:Simple' in rdf_string
    assert 'troll:x 42' in rdf_string