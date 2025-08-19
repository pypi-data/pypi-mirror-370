# JSONID

<!-- markdownlint-disable -->
<img
    src="https://github.com/ffdev-info/jsonid/blob/main/static/images/JSON_logo-crockford.png?raw=true"
    alt="JSON ID logo based on JSON Logo by Douglas Crockford"
    width="200px" />
<!-- markdownlint-enable -->

[**JSONID**][json-1]entification tool and ruleset. JSONID can be downloaded
from pypi.org.

[![PyPI - Version](https://img.shields.io/pypi/v/jsonid?style=plastic&color=purple)][pypi-json-id-1]

[json-1]: https://www.json.org/json-en.html
[pypi-json-id-1]: https://pypi.org/project/jsonid/

<!-- markdownlint-disable MD004 -->

## Contents

<!-- via: https://luciopaiva.com/markdown-toc/ -->

- [Before you begin...](#before-you-begin)
  - [MacOS](#macos)
  - [Windows](#windows)
  - [Linux](#linux)
- [Introduction to JSONID](#introduction-to-jsonid)
- [Why?](#why)
- [What does JSONID get you?](#what-does-jsonid-get-you)
- [Ruleset](#ruleset)
  - [Backed by tests](#backed-by-tests)
- [Sample files](#sample-files)
  - [Integration files](#integration-files)
  - [Fundamental examples](#fundamental-examples)
- [Registry](#registry)
  - [Registry examples](#registry-examples)
  - [Local rules](#local-rules)
- [PRONOM](#pronom)
- [Output format](#output-format)
- [JSONL](#jsonl)
  - [Handling JSONL](#handling-jsonl)
- [Analysis](#analysis)
  - [Example analysis](#example-analysis)
  - [JSONL technical metadata](#jsonl-technical-metadata)
- [Utils](#utils)
  - [json2json](#json2json)
- [Docs](#docs)
- [Developer install](#developer-install)
  - [pip](#pip)
  - [tox](#tox)
  - [pre-commit](#pre-commit)
- [Packaging](#packaging)
  - [pyproject.toml](#pyprojecttoml)
  - [Versioning](#versioning)
  - [Local packaging](#local-packaging)
  - [Publishing](#publishing)

## Before you begin

JSONID should run out of the box but it can be difficult to get everything
running correctly across all platforms without some effort. Additional
install instructions are listed below before you dig into everything in
more detail.

### MacOS

* MacOS users may need to run `brew install libmagic` to install libmagic
dependencies associated with compressed JSONL.

### Windows

* There are no known exceptions for Windows at present, that being said
an absence of libmagic on Windows means compressed JSONL cannot be
identified just yet.

### Linux

* There are no known exceptions for Linux users.

## Introduction to JSONID

JSONID borrows from the Python approach to ask forgiveness rather than
permission (EAFP) to attempt to open every object it scans and see if it
parses as JSON. If it doesn't, we move along. If it does, we then have an
opportunity to identify the characteristics of the JSON we have opened.

Python being high-level also provides an easier path to processing files
and parsing JSON quickly with very little other knowledge required
of the underlying data structure.

## Why?

Consider these equivalent forms:

```json
{
    "key 1": "value",
    "key 2": "value"
}
```

```json
{
    "key 2": "value",
    "key 1": "value"
}
```

PRONOM signatures are not expressive enough for complicated JSON objects.

If I want DROID to find `key 1` I have to use a wildcard, so I would write
something like:

```text
BOF: "7B*226B6579203122"
EOF: "7D"
```

But if I then want to match on `key 2` as well as `key 1` things start getting
complicated as they aren't guaranteed by the JSON specification to be in the
same "position" (if we think about order visually). When other keys are used in
the object they aren't even guaranteed to be next to one another.

This particular example is a 'map' object whose most important property
is consistent retrieval of information through its "keys". Further
complexity can be added when we are dealing with maps embedded in a "list" or
"array", or simply just maps of arbitrary depth.

JSONID tries to compensate for JSON's complexities by using the format's
own strengths to parse binary data as JSON and then if is successful,
use a JSON-inspired grammar to describe keys and key-value pairs as "markers"
that can potentially identify the JSON objects that we are looking at.
Certainly narrow down the potential instances of JSON objects that we might
be looking at.

## What does JSONID get you?

To begin, JSONID should identify JSON files on your system as JSON.
That's already a pretty good position to be in.

The ruleset should then allow you to identify a decent number of JSON objects,
especially those that have a well-defined structure. Examples we have in the
[registry data][registry-htm-1] include things like ActivityPub streams,
RO-CRATE metadata, IIIF API data and so on.

If the ruleset works for JSON we might be able to apply it to other formats
that can represent equivalent data structures in the future
such as [YAML][yaml-spec], and [TOML][toml-spec].

[yaml-spec]: https://yaml.org/
[toml-spec]: https://toml.io/en/

## Ruleset

JSONID currently defines a small set of rules that help us to identify JSON
documents.

The rules are described in their own data-structures. The structures are
processed as a list (they need not necessarily be in order) and each must
match for a given set of ruls to determine what kind of JSON document we might
be looking at.

JSONID can identify the existence of information but you can also use
wildcards and provide some negation as required, e.g. to remove
false-positives between similar JSON entities.

| rule       | meaning                                               |
|------------|-------------------------------------------------------|
| INDEX      | index (from which to read when structure is an array) |
| GOTO       | goto key (read key at given key)                      |
| KEY        | key to read                                           |
| CONTAINS   | value contains string                                 |
| STARTSWITH | value startswith string                               |
| ENDSWITH   | value endswith string                                 |
| IS         | value matches exactly                                 |
| REGEX      | value matches a regex pattern                         |
| EXISTS     | key exists                                            |
| NOEXIST    | key doesn't exists                                    |
| ISTYPE     | key is a specific type (string, number, dict, array)  |

Stored in a list within a `RegistryEntry` object, they are then processed
in order.

For example:

```json
    [
        { "KEY": "name", "IS": "value" },
        { "KEY": "schema", "CONTAINS": "/schema/version/1.1/" },
        { "KEY": "data", "IS": { "more": "data" } },
    ]
```

All rules need to match for a positive ID.

> **NB.**: JSONID is a
work-in-progress and requires community input to help determine the grammar
in its fullness and so there is a lot of opportunity to add/remove to these
methods as its development continues. Additionally, help formalizing the
grammar/ruleset would be greatly appreciated 🙏.

### Backed by tests

The ruleset has been developed using test-driven-development practices (TDD)
and the current set of tests can be reviewed in the repository's
[test folder][testing-1]. More tests should be added, in general, and over
time.

[testing-1]: https://github.com/ffdev-info/jsonid/tree/main/tests

## Sample files

### Integration files

Files used in the development of JSONID are available in their
[own repository][integration-1].

[integration-1]: https://github.com/ffdev-info/jsonid-integration-files

### Fundamental examples

There is a small [samples directory][samples-1] included with this
epository demonstrating some fundamental differences in encoding and
JSON types.

[samples-1]: samples/

## Registry

A temporary "registry" module is used to store JSON markers.
The registry is a work in progress and must be exported and
rewritten somewhere more centralized (and easier to manage) if JSONID can
prove useful to the communities that might use it (*see notes on PRONOM below*).

The registry web-page is here:

* [JSONID registry][registry-htm-1].

[registry-htm-1]: https://ffdev-info.github.io/jsonid/registry/

The registry's source is here:

* [Registry](https://github.com/ffdev-info/jsonid/blob/main/src/jsonid/registry_data.py).

### Registry examples

#### Identifying JSON-LD Generic

```python
    RegistryEntry(
        identifier="id0009",
        name=[{"@en": "JSON-LD (generic)"}],
        markers=[
            {"KEY": "@context", "EXISTS": None},
            {"KEY": "id", "EXISTS": None},
        ],
    ),
```

> **Pseudo code**:
Test for the existence of keys: `@context` and `id` in the primary JSON object.

#### Identifying Tika Recursive Metadata

```python
    RegistryEntry(
        identifier="id0024",
        name=[{"@en": "tika recursive metadata"}],
        markers=[
            {"INDEX": 0, "KEY": "Content-Length", "EXISTS": None},
            {"INDEX": 0, "KEY": "Content-Type", "EXISTS": None},
            {"INDEX": 0, "KEY": "X-TIKA:Parsed-By", "EXISTS": None},
            {"INDEX": 0, "KEY": "X-TIKA:parse_time_millis", "EXISTS": None},
        ],
```

> **Pseudo code**:
Test for the existence of keys: `Content-Length`, `Content-Type`,
`X-TIKA:Parsed-By` and `X-TIKA:parse_time_millis` in the `zeroth` (first)
JSON object where the primary document is a list of JSON objects.

#### Identifying SOPS encrypted secrets file

```python
    RegistryEntry(
        identifier="id0012",
        name=[{"@en": "sops encrypted secrets file"}],
        markers=[
            {"KEY": "sops", "EXISTS": None},
            {"GOTO": "sops", "KEY": "kms", "EXISTS": None},
            {"GOTO": "sops", "KEY": "pgp", "EXISTS": None},
        ],
    ),
```

> **Pseudo code**:
Test for the existence of keys `sops` in the primary JSON object.
>
> Goto the `sops` key and test for the existence of keys: `kms` and `pgp`
within the `sops` object/value.

### Local rules

The plan is to allow local rules to be run alongside the global ruleset. I
expect this will be a bit further down the line when the ruleset and
metaddata is more stabilised.

## PRONOM

Ideally JSON can generate evidence enough to warrant the creration of
PRONOM IDs that can then be referenced in the JSONID output.

Evantually, PRONOM or a PRONOM-like tool might host an authoritative version
of the JSONID registry.

## Output format

For ease of development, the utility currently outputs `yaml`. The structure
is still very fluid, and will also vary depending on the desired level of
detail in the registry, e.g. there isn't currently a lot of information about
the contents beyond a basic title and identifier.

E.g.:

```yaml
---
jsonid: 0.0.0
scandate: 2025-04-21T18:40:48Z
---
file: integration_files/plain.json
additional:
- '@en': data is dict type
depth: 1
documentation:
- archive_team: http://fileformats.archiveteam.org/wiki/JSON
identifiers:
- rfc: https://datatracker.ietf.org/doc/html/rfc8259
- pronom: http://www.nationalarchives.gov.uk/PRONOM/fmt/817
- loc: https://www.loc.gov/preservation/digital/formats/fdd/fdd000381.shtml
- wikidata: https://www.wikidata.org/entity/Q2063
mime:
- application/json
name:
- '@en': JavaScript Object Notation (JSON)
---
```

The structure should become more concrete as JSONID is formalized.

## JSONL

[JSONL][jsonl-1] aka JSON Lines is a format that requires some special
handling in the code, first to detect whether content is in an
"archive format" (archive in computer science terms) or aggregate (in
PRONOM terms); and then process the content reliably.

### Handling JSONL

JSONL will be treated as follows:

1. if a file is identified as JSONL a JSONL identification will always be
returned. This will always be reliable.
1. the first line of the JSONL file is treated as the authoritative object,
that is, all other lines are expected to conform to the same schema. If
the object can be matched against a ruleset the ID will be returned. If the
object cannoot be matched against a ruleset then an identification of
JSONL will be returned. All other lines are ignored.

[jsonl-1]: https://jsonlines.org/

## Analysis

JSONID provides an analysis mechanism to help developers of identifiers. It
might also help users talk about interesting properties about the objects
being analysed, and provide consistent fingerprinting for data that has
different byte-alignment but is otherwise identical.

> **NB.**: Comments on existing statistics or ideas for new ones are
appreciated.

### Example analysis

```json
{
  "content_length": 329,
  "number_of_lines": 32,
  "line_warning": false,
  "top_level_keys_count": 4,
  "top_level_keys": [
    "key1",
    "key2",
    "key3",
    "key4"
  ],
  "top_level_types": [
    "list",
    "map",
    "list",
    "list"
  ],
  "depth": 8,
  "heterogeneous_list_types": true,
  "fingerprint": {
    "unf": "UNF:6:sAsKNmjOtnpJtXi3Q6jVrQ==",
    "cid": "bafkreibho6naw5r7j23gxu6rzocrud4pc6fjsnteyjveirtnbs3uxemv2u"
  },
  "encoding": "UTF-8"
}
```

### JSONL technical metadata

Analysing JSONL should yield some useful information. Like many of the
analyses output by this tool this information is a work in progress and
time will tell if its useful.

#### Line length

Line length might not be a useful output for JSONL as the specification
itself determines JSONL files are very likely to have long lines. The
output is therefore disabled.

#### Fingerptinting

Fingreprinting JSONL versus standard JSON is done by treating the
JSONL file as a list of objects in memory. An important distinction to make is
that while this is technically correct, it's not structurally correct, i.e.
a JSONL file is not serialized as a list, nor, need it be deserialized into
memory as a `list` object. That being said, using a list structure in JSONID
as a small concession enabling fingerprinting makes it a convenient choice
and I hope it will prove beneficial.

#### Example JSONL analysis

JSONL analysis output is, therefore, a little more sparse than the
standard JSONID output, an example, at present, looks as follows:

```json
{
  "number_of_lines": 4,
  "fingerprint": {
    "unf": "UNF:6:iBedoWLhyVzfXOM0OcXWBg==",
    "cid": "bafkreigjgec7pbdao3ilk2pqe3tp3qg5bu426wyebnrelbm34ebhcbxs6q"
  },
  "doctype": "JSONL",
  "encoding": "UTF-8",
  "compression": "application/gzip"
}
```

## Utils

### json2json

UTF-16 can be difficult to read as UTF-16 uses two bytes per every one, e.g.
`..{.".a.".:. .".b.".}.` is simply `{"a": "b"}`. The utility `json2json.py`
in the utils folder will output UTF-16 as UTF-8 so that signatures can be
more easily derived. A signature derived for UTF-16 looks exactly the same
as UTF-8.

`json2json` can be called from the command line when installed via pip, or
find it in [src.utils][json2json-1].

[json2json-1]: src/utils/json2json.py

## Docs

Dev docs are [available][dev-docs-1].

[dev-docs-1]: https://ffdev-info.github.io/jsonid/jsonid/

----

## Developer install

### pip

Setup a virtual environment `venv` and install the local development
requirements as follows:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements/local.txt
```

### tox

#### Run tests (all)

```bash
python -m tox
```

#### Run tests-only

```bash
python -m tox -e py3
```

#### Run linting-only

```bash
python -m tox -e linting
```

### pre-commit

Pre-commit can be used to provide more feedback before committing code. This
reduces reduces the number of commits you might want to make when working on
code, it's also an alternative to running tox manually.

To set up pre-commit, providing `pip install` has been run above:

* `pre-commit install`

This repository contains a default number of pre-commit hooks, but there may
be others suited to different projects. A list of other pre-commit hooks can be
found [here][pre-commit-1].

[pre-commit-1]: https://pre-commit.com/hooks.html

## Packaging

The [`justfile`][just-1] contains helper functions for packaging and release.
Run `just help` for more information.

[just-1]: https://github.com/casey/just

### pyproject.toml

Packaging consumes the metadata in `pyproject.toml` which helps to describe
the project on the official [pypi.org][pypi-2] repository. Have a look at the
documentation and comments there to help you create a suitably descriptive
metadata file.

### Versioning

Versioning in Python can be hit and miss. You can label versions for
yourself, but to make it reliaable, as well as meaningful is should be
controlled by your source control system. We assume git, and versions can
be created by tagging your work and pushing the tag to your git repository,
e.g. to create a release candidate for version 1.0.0:

```sh
git tag -a 1.0.0-rc.1 -m "release candidate for 1.0.0"
git push origin 1.0.0-rc.1
```

When you build, a package will be created with the correct version:

```sh
just package-source
### build process here ###
Successfully built python_repo_jsonid-1.0.0rc1.tar.gz and python_repo_jsonid-1.0.0rc1-py3-none-any.whl
```

### Local packaging

To create a python wheel for testing locally, or distributing to colleagues
run:

* `just package-source`

A `tar` and `whl` file will be stored in a `dist/` directory. The `whl` file
can be installed as follows:

* `pip install <your-package>.whl`

### Publishing

Publishing for public use can be achieved with:

* `just package-upload-test` or `just package-upload`

`just-package-upload-test` will upload the package to [test.pypi.org][pypi-1]
which provides a way to look at package metadata and documentation and ensure
that it is correct before uploading to the official [pypi.org][pypi-2]
repository using `just package-upload`.

[pypi-1]: https://test.pypi.org
[pypi-2]: https://pypi.org
