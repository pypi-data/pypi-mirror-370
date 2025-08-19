"""Implements pyproject.toml."""

from pathlib import Path

import tomli

from pyvelocity.configurations.files import ConfigurationFile
from pyvelocity.configurations.files.sections.black import Black
from pyvelocity.configurations.files.sections.docformatter import Docformatter
from pyvelocity.configurations.files.sections.factory import PyProjectTomlSectionFactory
from pyvelocity.configurations.files.sections.flake8 import Flake8
from pyvelocity.configurations.files.sections.isort import Isort
from pyvelocity.configurations.files.sections.pylint import PyProjectTomlPylintFactory
from pyvelocity.configurations.files.sections.pyvelocity import Pyvelocity
from pyvelocity.configurations.files.sections.ruff import Ruff

WHERE_PY_PROJECT_TOML = "pyproject.toml"


class PyProjectToml(ConfigurationFile):
    """pyproject.toml."""

    def __init__(self, path_py_project_toml: Path) -> None:
        super().__init__()
        parsed_toml = tomli.loads(path_py_project_toml.read_text(encoding="utf-8"))
        node_tool = "tool"
        tool = parsed_toml[node_tool]
        self.black = PyProjectTomlSectionFactory.create(self, node_tool, Black, tool)
        self.docformatter = PyProjectTomlSectionFactory.create(self, node_tool, Docformatter, tool)
        self.flake8 = PyProjectTomlSectionFactory.create(self, node_tool, Flake8, tool)
        self.isort = PyProjectTomlSectionFactory.create(self, node_tool, Isort, tool)
        self.pylint = PyProjectTomlPylintFactory.create(self, node_tool, tool)
        self.pyvelocity = PyProjectTomlSectionFactory.create(self, node_tool, Pyvelocity, tool)
        self.ruff = PyProjectTomlSectionFactory.create(self, node_tool, Ruff, tool)

    @property
    def name(self) -> str:
        return WHERE_PY_PROJECT_TOML
