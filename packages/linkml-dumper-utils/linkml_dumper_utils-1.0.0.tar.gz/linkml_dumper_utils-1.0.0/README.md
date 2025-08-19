# LinkML Dumper Utils

This is a small helper package to get the dumping with linkml models more aligned
with the practices of pydantic and Python dataclasses.
Namely, using model_dump_* and as* methods.
Moreover, some tooling to directly add linkml schema objects to your classes is included
to be able to produce different serializations out of the box.

At the moment the serialization is supported for both JsonLD and RDF.
However, the JSON LD implementation is not actually using the linkml runtime dumpers,
but replicates some of its functionality but in a more convenient way.

## Installation

`pip install linkml-dumper-utils`

## Example usage

```python
from pydantic import BaseModel
from linkml_dumper_utils.pydantic import PydanticJsonldMixin

class MyClass(BaseModel, PydanticJsonldMixin, context_file_path='myContext.json'):
    name: str


obj = MyClass(name='Bob')

jsonld = obj.model_dump_jsonld()
```

Considering the context of `myContext.json` looks like the following

```json
{
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dct": "http://purl.org/dc/terms/",
    "Person": "foaf:Person",
    "name": "dct:title"
}
```

The jsonld object above would be a Python dict looking like this:

```json
{
    "@context": {
        "foaf": "http://xmlns.com/foaf/0.1/",
        "dct": "http://purl.org/dc/terms/",
        "Person": "foaf:Person",
        "name": "dct:title"
    },
    "@type": "Person",
    "name": "Bob"
}
```

The context for a class can be specified in three ways:

- context_file_path
- context_string (also works as context URL - if double quoted)
- context (as a dict)

Next to JSON LD there is also the mixin for rdf data.
It works exactly the same however, the arguments for class creation now include
the following three options:

- schema_file_path
- schema_string (YAML or JSON as a string variable)
- schema_view (from linkml runtime)

## Usage for pydantic

The following methods have been added to your pydantic classes depending on the used mixin:

- PydanticJsonldMixin
  - model_dump_jsonld
  - model_dump_jsonld_string
- PydanticRdflibMixin
  - model_dump_rdflib_graph
  - model_dump_rdf_string

There are several ways how this package can be used to interact with both existing
pydantic models that can not be modified and your own pydantic models that you can
simply update to reflect what you need.

### Pydantic model using mixin via inheritance

```python
from pydantic import BaseModel
from linkml_dumper_utils.pydantic import PydanticJsonldMixin

class MyClass(BaseModel, PydanticJsonldMixin, context_file_path='myContext.json'):
    ...
```

### Pydantic model using decorator
```python
from pydantic import BaseModel
from linkml_dumper_utils.pydantic import pydantic_rdflib_mixin

@pydantic_rdflib_mixin(schema_file_path='myModel.yaml')
class MyClass(BaseModel):
    ...
```

### Pydantic with manual decoration

```python
from pydantic import BaseModel
from linkml_dumper_utils.pydantic import pydantic_rdflib_mixin

class MyClass(BaseModel):
    ...

MyClass = pydantic_rdflib_mixin(schema_file_path='myModel.yaml')(MyClass)
```

### Pydantic replacing third party models

Sometimes you would want to create a wrapper module to encapsulate certain classes from
a third party module.

I recommend something like the following (though I have not explicity tested it).

Create a file wrapper.py to contain the modified class definitions so you can then use `from wrapper import ClassA`.

```python
import third_party  # use whatever module you want to modify

from linkml_dumper_utils.pydantic import pydantic_jsonld_mixin

for name in dir(third_party):
    obj = getattr(third_party, name)
    globals()[name] = pydantic_jsonld_mixin(context_file_path='myContext.json')(obj)
```
Of course, this is a little hacky but it might just do the trick depending on your context.

## Usage for dataclasses

The behavior options are exactly the same for dataclasses.

However, the usage pattern for the actual dumpers is different in dataclasses.
As they do not use member functions as dumpers but global functions that receive 
the object to be dumped as the first argument.

The available methods are:

- DataclassJsonldMixin
  - as_json_string
  - as_json_ld
  - as_json_ld_string
- DataclassRdflibMixin
  - as_rdflib_graph
  - as_rdf_string

Example

```python
from dataclasses import dataclass

from linkml_dumper_utils.dataclass import DataclassJsonldMixin, as_json_ld

@dataclass
class MyClass(DataclassJsonldMixin, context_file_path='my_context.json'):
  x: int
  
test = MyClass(x=42)

data = as_json_ld(test)

```