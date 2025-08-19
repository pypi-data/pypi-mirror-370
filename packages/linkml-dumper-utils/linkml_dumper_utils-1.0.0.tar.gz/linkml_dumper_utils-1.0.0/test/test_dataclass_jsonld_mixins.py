from dataclasses import dataclass, asdict

from linkml_runtime.dumpers import json_dumper
from linkml_runtime.utils.yamlutils import as_json_object, YAMLRoot

from linkml_dumper_utils.dataclass import dataclass_jsonld_mixin, as_json_ld, DataclassJsonldMixin, as_json_ld_string


def test_jsonld_mixin_with_decoration():
    context = '{"x": "https://some.url/x"}'

    @dataclass_jsonld_mixin(context_string=context)
    @dataclass
    class Simple:
        x: int

    s = Simple(x=42)
    dump = as_json_ld(s)
    assert '@context' in dump


def test_jsonld_mixin_with_manual_decorator_call():
    context = '{"x": "https://some.url/x"}'

    @dataclass
    class Simple:
        x: int

    s = Simple(x=42)

    Simple = dataclass_jsonld_mixin(context_string=context)(Simple)

    s2 = Simple(x=42)

    dump = asdict(s)
    dump2 = asdict(s2)
    dump3 = as_json_ld(s2)
    assert '@context' not in dump
    assert '@context' not in dump2
    assert '@context' in dump3


def test_jsonld_mixin_with_decoration_separate_contexts():
    context_a = {'x': 'a'}
    context_b = {'x': 'b'}

    @dataclass_jsonld_mixin(context=context_a)
    @dataclass
    class SimpleA:
        x: int

    @dataclass_jsonld_mixin(context=context_b)
    @dataclass
    class SimpleB:
        x: int

    sa = SimpleA(x=42)
    sb = SimpleB(x=42)

    dump_a = as_json_ld(sa)
    dump_b = as_json_ld(sb)

    assert dump_a['@context']['x'] == 'a'
    assert dump_b['@context']['x'] == 'b'


def test_jsonld_mixin_inheritance():
    context = '{"x": "https://some.url/x"}'

    @dataclass
    class Simple(DataclassJsonldMixin, context_string=context):
        x: int

    s = Simple(x=42)
    dump = asdict(s)
    dump2 = as_json_ld(s)
    assert '@context' not in dump
    assert '@context' in dump2


def test_jsonld_structure():
    context = {
        "foaf": "http://xmlns.com/foaf/0.1/",
        "dct": "http://purl.org/dc/terms/",
        "Person": "foaf:Person",
        "name": "dct:title"
    }

    @dataclass
    class Person(YAMLRoot, DataclassJsonldMixin, context=context):
        name: str

    bob = Person(name='bob')

    dump = as_json_ld(bob)
    assert '@context' in dump
    assert '@type' in dump

    # jsonld = as_json_ld_string(bob)
    #
    # non_semantic_dump = asdict(bob)
    #
    # element_type = bob.__class__.__name__
    # non_semantic_dump2 = as_json_object(non_semantic_dump, context, element_type)
    # dump2 = json_dumper.dumps(non_semantic_dump, contexts=context)
    # _ = 42
