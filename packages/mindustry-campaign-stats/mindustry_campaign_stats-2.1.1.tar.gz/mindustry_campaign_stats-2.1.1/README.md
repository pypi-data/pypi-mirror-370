# Mindustry Campaign Stats

Python API and CLI tool to read [Mindustry](https://mindustrygame.github.io/)'s campaign global stats.

![Python versions](https://img.shields.io/pypi/pyversions/mindustry-campaign-stats.svg) ![Version](https://img.shields.io/pypi/v/mindustry-campaign-stats.svg) ![License](https://img.shields.io/pypi/l/mindustry-campaign-stats.svg)

[PyPI](https://pypi.org/project/mindustry-campaign-stats/) - [Documentation](https://github.com/EpocDotFr/mindustry-campaign-stats?tab=readme-ov-file#usage) - [Source code](https://github.com/EpocDotFr/mindustry-campaign-stats) - [Issue tracker](https://github.com/EpocDotFr/mindustry-campaign-stats/issues) - [Changelog](https://github.com/EpocDotFr/mindustry-campaign-stats/releases)

## Prerequisites

  - Python >= 3.10

## Installation

### From PyPi

```shell
pip install mindustry-campaign-stats
```

### Locally

After cloning/downloading the repo:

```shell
pip install .
```

## Usage

### API

The API consists of:

  - A `load()` function, which reads data from the given binary file-like object and returns the raw parsed data as
    a dictionary
  - A `compute()` function, which transforms the above dictionary to a
    [`Stats`](https://github.com/EpocDotFr/mindustry-campaign-stats/blob/master/mindustry_campaign_stats/stats.py) instance
  - A `Planet` enum (`Serpulo`, `Erekir`) to be used with `compute()`

```python
import mindustry_campaign_stats
from pprint import pprint

try:
    with open('settings.bin', 'rb') as fp: # Note it's opened in binary mode
        raw_settings = mindustry_campaign_stats.load(fp)

    pprint(raw_settings)

    computed = mindustry_campaign_stats.compute(
        raw_settings,
        mindustry_campaign_stats.Planet.Erekir
    )

    print(computed.totals.storage.capacity)

    pprint(
      computed.to_dict()
    )
except Exception as e:
    print(e)
```

### CLI

In its simplest form, the CLI reads data from the given `settings.bin` filename, then writes a human-readable ASCII table
of computed stats to `stdout`. Note you must choose between the `serpulo` or `erekir` campaign.

```shell
mindustry-campaign-stats settings.bin erekir
```

When the `--refresh` option is set, the CLI is running indefinitely, listening for modification in the given `settings.bin`
file until it's terminated. This feature allows the table to be automatically updated in your terminal (screen is cleared
before any update happens).

The `--json` option switches output format to JSON, specifically [JSON Lines](https://jsonlines.org/). The `--pretty`
option may be used to pretty-print the outputted JSON. When `--refresh` is set as well, the CLI will sequentially write
a stream of JSON Lines. Note that `--pretty` is ignored in that case as it would break JSON Lines formatting.

## `settings.bin` format

This file is designed much like a persistent key-value store. It is used to store both user settings and campaigns-related
data. It is formatted as follows (everything is big-endian):

- 4 bytes (int32) - Number of fields to read (`fields_count`)
- Fields sequence (based on `fields_count`):
  - 2 bytes (uint16) - Length of the field name (`field_name_length`)
  - `field_name_length` bytes - [MUTF-8](https://en.wikipedia.org/wiki/UTF-8#Modified_UTF-8)-encoded field name
  - 1 byte (int8) - Field type ID (`field_type_id`)
  - `field_type_id` value determines how to read the next bytes:
    - `0`:
      - 1 byte (boolean) - A boolean value
    - `1`:
      - 4 bytes (int32) - A 32 bits integer
    - `2`:
      - 8 bytes (int64) - A 64 bits integer
    - `3`:
      - 4 bytes (float) - A single-precision floating-point number
    - `4`:
      - 2 bytes (uint16) - Length of the field value (`field_value_length`)
      - `field_value_length` bytes - An [MUTF-8](https://en.wikipedia.org/wiki/UTF-8#Modified_UTF-8)-encoded string
    - `5`:
      - 4 bytes (int32) - Length of the field value (`field_value_length`)
      - `field_value_length` bytes - A binary value. Most likely [UBJSON](https://en.wikipedia.org/wiki/UBJSON) data

## References

  - [Settings.java](https://github.com/Anuken/Arc/blob/v149/arc-core/src/arc/Settings.java)
  - [SectorPresets.java](https://github.com/Anuken/Mindustry/blob/v149/core/src/mindustry/content/SectorPresets.java)
  - [Items.java](https://github.com/Anuken/Mindustry/blob/v149/core/src/mindustry/content/Items.java)

## Development

### Getting source code and installing the package with dev dependencies

  1. Clone the repository
  2. From the root directory, run: `pip install -e ".[dev]"`

### Releasing the package

From the root directory, run `python setup.py upload`. This will build the package, create a git tag and publish on PyPI.

`__version__` in `mindustry_campaign_stats/__version__.py` must be updated beforehand. It should adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

An associated GitHub release must be created following the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.
