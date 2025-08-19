from pydantic import BaseModel

from linkml_dumper_utils.pydantic import pydantic_jsonld_mixin, PydanticJsonldMixin


def test_jsonld_mixin_with_decoration():
    

    context = '{"x": "https://some.url/x"}'
    @pydantic_jsonld_mixin(context_string=context)
    class Simple(BaseModel):
        x: int

    s = Simple(x = 42)
    dump = s.model_dump_jsonld()
    assert '@context' in dump


def test_jsonld_mixin_with_manual_decorator_call():
    context = '{"x": "https://some.url/x"}'

    class Simple(BaseModel):
        x: int

    s = Simple(x = 42)

    Simple = pydantic_jsonld_mixin(context_string=context)(Simple)

    s2 = Simple(x = 42)

    dump = s.model_dump()
    dump2 = s2.model_dump()
    dump3 = s2.model_dump_jsonld()
    assert '@context' not in dump
    assert '@context' not in dump2
    assert '@context' in dump3


def test_jsonld_mixin_with_decoration_separate_contexts():
    context_a = {'x': 'a'}
    context_b = {'x': 'b'}

    @pydantic_jsonld_mixin(context=context_a)
    class SimpleA(BaseModel):
        x: int


    @pydantic_jsonld_mixin(context=context_b)
    class SimpleB(BaseModel):
        x: int

    sa = SimpleA(x = 42)
    sb = SimpleB(x = 42)

    dump_a = sa.model_dump_jsonld()
    dump_b = sb.model_dump_jsonld()

    assert dump_a['@context']['x'] == 'a'
    assert dump_b['@context']['x'] == 'b'


def test_jsonld_mixin_inheritance():
    context = '{"x": "https://some.url/x"}'

    class Simple(BaseModel, PydanticJsonldMixin, context_string=context):
        x: int

    s = Simple(x=42)
    dump = s.model_dump()
    dump2 = s.model_dump_jsonld()
    assert '@context' not in dump
    assert '@context' in dump2


def test_jsonld_structure():
    context = {
        "foaf": "http://xmlns.com/foaf/0.1/",
        "dct": "http://purl.org/dc/terms/",
        "Person": "foaf:Person",
        "name": "dct:title"
    }

    class Person(BaseModel, PydanticJsonldMixin, context=context):
        name: str

    bob = Person(name='bob')

    dump = bob.model_dump_jsonld()
    assert '@context' in dump
