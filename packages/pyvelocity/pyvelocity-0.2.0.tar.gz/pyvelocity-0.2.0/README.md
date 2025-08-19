# pyvelocity

[![Test](https://github.com/yukihiko-shinoda/pyvelocity/workflows/Test/badge.svg)](https://github.com/yukihiko-shinoda/pyvelocity/actions?query=workflow%3ATest)
[![CodeQL](https://github.com/yukihiko-shinoda/pyvelocity/workflows/CodeQL/badge.svg)](https://github.com/yukihiko-shinoda/pyvelocity/actions?query=workflow%3ACodeQL)
[![Code Coverage](https://qlty.sh/gh/yukihiko-shinoda/projects/pyvelocity/coverage.svg)](https://qlty.sh/gh/yukihiko-shinoda/projects/pyvelocity)
[![Maintainability](https://qlty.sh/gh/yukihiko-shinoda/projects/pyvelocity/maintainability.svg)](https://qlty.sh/gh/yukihiko-shinoda/projects/pyvelocity)
[![Code Climate technical debt](https://img.shields.io/codeclimate/tech-debt/yukihiko-shinoda/pyvelocity)](https://codeclimate.com/github/yukihiko-shinoda/pyvelocity)
[![Python versions](https://img.shields.io/pypi/pyversions/pyvelocity.svg)](https://pypi.org/project/pyvelocity)
[![Twitter URL](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Fyukihiko-shinoda%2Fpyvelocity)](http://twitter.com/share?text=PyVelocity&url=https://pypi.org/project/pyvelocity/&hashtags=python)

Automates task to check configurations about Python project to follow best practices to increase development velocity.

## Attention

The development status of this package is Beta now. It may not be able to keep backward compatibility. Be careful to use, especially for CI.

## Check content

- line-length
- using-py-project-toml

### line-length

Checks if following settings are same:

- docformatter:
  - wrap-descriptions
  - wrap-summaries
- isort: line_length
- Black: line-length
- flake8: max-line-length
- Pylint: format: max-line-length

### using-py-project-toml

Checks if use pyproject.toml.

## Quickstart

### 1. Install

```console
pip install pyvelocity
```

### 2. Run command

Run following command at the directory which pyproject.toml and setup.cfg exists.

```console
pyvelocity
```

<!-- markdownlint-disable no-trailing-punctuation -->
## How do I...
<!-- markdownlint-enable no-trailing-punctuation -->

### Ignore specific check?

For examble, if you want to ignore the check: line-length, add following content into pyproject.toml:

```toml
[tool.pyvelocity]
filter = [
  "line-length"
]
```

## Credits

This package was created with [Cookiecutter] and the [yukihiko-shinoda/cookiecutter-pypackage] project template.

[Cookiecutter]: https://github.com/audreyr/cookiecutter
[yukihiko-shinoda/cookiecutter-pypackage]: https://github.com/yukihiko-shinoda/cookiecutter-pypackage
