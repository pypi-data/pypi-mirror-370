<h1 align="center">Panther Core</h1>

<p align="center">
  <i>Python core for Panther detections</i>
</p>

<p align="center">
  <a href="https://docs.runpanther.io">Documentation</a> |
  <a href="https://docs.runpanther.io/quick-start">Quick Start</a>
</p>

<p align="center">
  <a href="https://circleci.com/gh/panther-labs/panther_core"><img src="https://circleci.com/gh/panther-labs/panther_core.svg?style=svg" alt="CircleCI"/></a>
</p>

---

`panther_core` is a Python library for Panther Detections. See the
[Panther documentation](https://docs.runpanther.io/quick-start) for more details
on Panther.

# Installation

Install simply with pip:

```shell
pip3 install panther_core
```

## Build From Source

If you'd prefer instead to run from source for development reasons, first setup
your environment:

```shell
make install-pipenv
make install
pipenv run -- pip3 install -e .
```

If you would rather use the `panther_core` outside of the virtual environment,
install it directly:

```shell
make deps
pip3 install -e .
```

## Testing

Follow the build steps above, then run:

```shell
make test
```

## Publishing

See [notion](https://www.notion.so/pantherlabs/Release-Guide-panther-core-946a6bc1a1b34f1a93813a3378662375)

# Contributing

We welcome all contributions! Please read the
[contributing guidelines](https://github.com/panther-labs/panther_core/blob/master/CONTRIBUTING.md)
before submitting pull requests.
[Instructions for opening a pull request](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request)
from your fork of the repo can be found on Github.

## License

This repository is licensed under the AGPL-3.0
[license](https://github.com/panther-labs/panther_core/blob/master/LICENSE).
