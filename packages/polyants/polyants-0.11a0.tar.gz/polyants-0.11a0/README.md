# polyants

> POLYHUB system helpers.

[![pipeline status](https://gitlab.com/ru-r5/polyants/badges/master/pipeline.svg)](https://gitlab.com/ru-r5/polyants/-/commits/master)
[![PyPI version](https://badge.fury.io/py/polyants.png)](https://badge.fury.io/py/polyants)

![logo](polyants.png)

## Installation

OS X & Linux & Windows:

```sh
pip install polyants
```

## Usage example

```python
from polyants.polyhub.helpers.common import get_now

print(get_now())
```

## Development setup

- tool requirements:
  - poetry

- activating environment

```sh
poetry shell
```

- preparing environment

```sh
poetry install --no-root
```

- generating grpc artifacts

```sh
rm -rf ./polyants/polyhub/grpc/*
touch ./polyants/polyhub/grpc/__init__.py
python -m grpc_tools.protoc -I ./protos --python_out=./ --pyi_out=./ --grpc_python_out=./ ./protos/polyants/polyhub/grpc/*.proto
```

- coverage

```sh
poetry run pytest --cov
```

- format

```sh
poetry run black polyants -S
```

- lint

```sh
poetry run ruff check
```

- type checking

```sh
poetry run pyre --sequential
```

## Release History

- 0.11a0
  - workflow object type support (#51)
  - product object type support (#52)
  - report generator timeout support (#53)
  - internal token based API requests (#54)
  - data quality API support (#55)
  - platform aware path sanitizer (#56)
- 0.10a0
  - temp file context manager (#38)
  - telegram notification support (#45)
  - rate limiter integration (#46)
  - using lookup attribute dataType as default lookup key column type (#47)
  - support for alert attachments as parameters (#48)
  - support for adding and deleting historical records in datagrids with lookups (#49)
  - support for SMB storage (#50)
- 0.9a0
  - datagrid filters boolean values handling (#44)
  - catalog timeout error handling (#43)
  - `fix_base64_padding` function (#42)
  - `to_plain_json` should not sort target json attributes (#40)
  - `column` attribute should not be required for datagrid filter attributes (#39)
  - Visiology v3 API support (#37)
- 0.8a0
  - `SYNC_FILES` bucket token capability (#36)
- 0.7a0
  - `REPOSITORY` object type and auxiliary functions (#35)
- 0.6a0
  - float schema version number support (#34)
  - new object type `SCRIPT` and it's types (#35)
- 0.5a0
  - process_folder function without recursion (#29)
  - object settings caching (#30)
  - function to encode a string as urlsafe base64 (#31)
  - semi-automatically generation of `calculated` attribute in datagrid definitions (#32)
- 0.4a0
  - to_plain_json function to remove meta from json definitions (#28)
- 0.3a0
  - polyhub helpers starter bundle (#21)
- 0.2a0
  - configurable enum class (#3)
- 0.1a0
  - mvp (#1)

## Meta

<pymancer@gmail.com> ([Polyanalitika LLC](https://polyanalitika.ru))  
[https://gitlab.com/ru-r5/polyants](https://gitlab.com/ru-r5/polyants)

## License

This Source Code Form is subject to the terms of the Mozilla Public  
License, v. 2.0. If a copy of the MPL was not distributed with this  
file, You can obtain one at <https://mozilla.org/MPL/2.0/>.  

## Contributing

1. Fork it (<https://gitlab.com/ru-r5/polyants/fork>)
2. Create your feature branch (`git checkout -b feature/foo`)
3. Commit your changes (`git commit -am 'Add some foo'`)
4. Push to the branch (`git push origin feature/foo`)
5. Create a new Pull Request
