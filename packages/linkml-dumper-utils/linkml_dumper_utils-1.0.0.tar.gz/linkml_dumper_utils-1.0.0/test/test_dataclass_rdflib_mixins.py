from dataclasses import dataclass

import pytest

import personinfo
from linkml_dumper_utils.dataclass import dataclass_rdflib_mixin, as_rdf_string, DataclassRdflibMixin, as_json_string
from personinfo import EmploymentEvent, Organization


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
    @dataclass_rdflib_mixin(schema_string=simple_schema)
    @dataclass
    class Simple:
        x: int

    @dataclass_rdflib_mixin(schema_string=simple_schema.replace(' x:', ' y:').replace('Simple:', 'Simple2:'))
    @dataclass
    class Simple2:
        y: int

    s = Simple(x=42)
    s2 = Simple2(y=21)

    rdf_string = as_rdf_string(s)
    rdf_string2 = as_rdf_string(s2)

    assert '[] a troll:Simple' in rdf_string
    assert 'troll:x 42' in rdf_string


def test_linkml_rdflib_mixin_inheritance(simple_schema):
    @dataclass
    class Simple(DataclassRdflibMixin, schema_string=simple_schema):
        x: int

    s = Simple(x=42)
    rdf_string = as_rdf_string(s)

    assert '[] a troll:Simple' in rdf_string
    assert 'troll:x 42' in rdf_string


# def test_person_info_demo_data():
#     Container = dataclass_rdflib_mixin(schema_file_path='test/data/personinfo.yaml')(personinfo.Container)
#     Organization = dataclass_rdflib_mixin(schema_file_path='test/data/personinfo.yaml')(personinfo.Organization)
#     Person = dataclass_rdflib_mixin(schema_file_path='test/data/personinfo.yaml')(personinfo.Person)
#     EmploymentEvent = dataclass_rdflib_mixin(schema_file_path='test/data/personinfo.yaml')(personinfo.EmploymentEvent)
#
#     org = Organization(
#         id='ROR:1',
#         name='foo'
#     )
#     p1 = Person(id='P:001', name='fred bloggs', primary_email='fred.bloggs@example.com', age_in_years=33)
#     p2 = Person(
#         id='P:002',
#         name='joe schmoe',
#         primary_email='joe.schmoe@example.com',
#         has_employment_history=[
#             EmploymentEvent(
#                 employed_at=org,
#                 started_at_time='2019-01-01',
#                 is_current=True
#             ),
#         ]
#     )
#
#     container = Container(
#         persons=[p1, p2],
#         organizations=[org]
#     )
#
#     rdf_string = as_rdf_string(p2)
#
#     assert 'personinfo:employed_at ROR:1' in rdf_string
