[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)
[![Actions status](https://github.com/lab-sync/biosero-data-services-sdk/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/lab-sync/biosero-data-services-sdk/actions)
[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/lab-sync/biosero-data-services-sdk)
[![PyPI Version](https://img.shields.io/pypi/v/biosero-data-services-sdk.svg)](https://pypi.org/project/biosero-data-services-sdk/)
[![Downloads](https://pepy.tech/badge/biosero-data-services-sdk)](https://pepy.tech/project/biosero-data-services-sdk)
[![Python Versions](https://img.shields.io/pypi/pyversions/biosero-data-services-sdk.svg)](https://pypi.org/project/biosero-data-services-sdk/)
[![Codecov](https://codecov.io/gh/lab-sync/biosero-data-services-sdk/branch/main/graph/badge.svg)](https://codecov.io/gh/lab-sync/biosero-data-services-sdk)

# Usage
Documentation is hosted on [ReadTheDocs](https://biosero-data-services-sdk.readthedocs.io/en/latest/?badge=latest).

# Development
This project has a dev container. If you already have VS Code and Docker installed, you can click the badge above or [here](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/lab-sync/biosero-data-services-sdk) to get started. Clicking these links will cause VS Code to automatically install the Dev Containers extension if needed, clone the source code into a container volume, and spin up a dev container for use.

To publish a new version of the repository, you can run the `Publish` workflow manually and publish to the staging registry from any branch, and you can check the 'Publish to Primary' option when on `main` to publish to the primary registry and create a git tag.

Open a connection to the EC2 instance hosting GBG Data Services in AWS:
```bash
aws ssm start-session --target i-0e5fd6d0bcdfd3c03 --document-name AWS-StartPortForwardingSession --parameters '{"portNumber":["8105"],"localPortNumber":["8105"]}'
```

When running the unit test suite, `pytest-recording` library is used. If it gives you errors about a cassette missing, the parameter to invoke a live HTTP request is `--record-mode=once` (add on to the end of the `pytest` command)



## Updating from the template
This repository uses a copier template. To pull in the latest updates from the template, use the command:
`copier update --trust --conflict rej --defaults`
