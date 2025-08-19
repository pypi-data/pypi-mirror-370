<div align="center">

# tap-socketdev

<div>
  <a href="https://results.pre-commit.ci/latest/github/edgarrmondragon/tap-socketdev/main">
    <img alt="pre-commit.ci status" src="https://results.pre-commit.ci/badge/github/edgarrmondragon/tap-socketdev/main.svg"/>
  </a>
  <a href="https://github.com/edgarrmondragon/tap-socketdev/blob/main/LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/edgarrmondragon/tap-socketdev"/>
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;">
  </a>
  <a href="https://pypi.org/p/tap-socketdev/">
    <img alt="Python versions" src="https://img.shields.io/pypi/pyversions/tap-socketdev"/>
  </a>
</div>

Singer tap for [socket.dev](https://socket.dev).

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

</div>

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`

## Settings

| Setting    | Required | Default | Description                        |
| :--------- | :------- | :------ | :--------------------------------- |
| api_key    | True     | None    | API Key for Socket                 |
| start_date | False    | None    | Earliest datetime to get data from |

A full list of supported settings and capabilities is available by running: `tap-socketdev --about`

### Builtin Settings

The following settings are available to all taps.

| Setting                           | Required | Default | Description                                                                                                                                                                                                                                               |
| :-------------------------------- | :------- | :------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| stream_maps                       | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html).                                                                                                               |
| stream_map_config                 | False    | None    | User-defined config values to be used within map expressions.                                                                                                                                                                                             |
| faker_config                      | False    | None    | Config for the [`Faker`](https://faker.readthedocs.io/en/master/) instance variable `fake` used within map expressions. Only applicable if the plugin specifies `faker` as an additional dependency (through the `singer-sdk` `faker` extra or directly). |
| faker_config.seed                 | False    | None    | Value to seed the Faker generator for deterministic output: https://faker.readthedocs.io/en/master/#seeding-the-generator                                                                                                                                 |
| faker_config.locale               | False    | None    | One or more LCID locale strings to produce localized output for: https://faker.readthedocs.io/en/master/#localization                                                                                                                                     |
| flattening_enabled                | False    | None    | 'True' to enable schema flattening and automatically expand nested properties.                                                                                                                                                                            |
| flattening_max_depth              | False    | None    | The max depth to flatten schemas.                                                                                                                                                                                                                         |
| batch_config                      | False    | None    | Configuration for BATCH message capabilities.                                                                                                                                                                                                             |
| batch_config.encoding             | False    | None    | Specifies the format and compression of the batch files.                                                                                                                                                                                                  |
| batch_config.encoding.format      | False    | None    | Format to use for batch files.                                                                                                                                                                                                                            |
| batch_config.encoding.compression | False    | None    | Compression format to use for batch files.                                                                                                                                                                                                                |
| batch_config.storage              | False    | None    | Defines the storage layer to use when writing batch files                                                                                                                                                                                                 |
| batch_config.storage.root         | False    | None    | Root path to use when writing batch files.                                                                                                                                                                                                                |
| batch_config.storage.prefix       | False    | None    | Prefix to use when writing batch files.                                                                                                                                                                                                                   |

### Source Authentication and Authorization

- [Creating and Managing API Tokens](https://docs.socket.dev/reference/creating-and-managing-api-tokens).

## Usage

You can easily run `tap-socketdev` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-socketdev --version
tap-socketdev --help
tap-socketdev --config CONFIG --discover > ./catalog.json
```

## Developer Resources

### Initialize your Development Environment

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # or see https://docs.astral.sh/uv/getting-started/installation/
uv sync
```

### Create and Run Tests

Create tests within the `tests` subfolder and then run:

```bash
uvx pytest
```

You can also test the `tap-socketdev` CLI interface directly using `uv run`:

```bash
uv run tap-socketdev --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
uv tool install meltano
# Initialize meltano within this directory
cd tap-socketdev
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-socketdev --version
# OR run a test EL pipeline:
meltano run tap-socketdev target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
