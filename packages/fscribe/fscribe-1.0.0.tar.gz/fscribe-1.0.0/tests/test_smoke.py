import pytest

from fscribe.configuration import ConfigurationManager
from fscribe.core import ProjectAnalysisService


def test_configuration_defaults():
    cm = ConfigurationManager(None, None)
    includes = cm.get_include_patterns()
    assert isinstance(includes, list)
    assert len(includes) > 0


def test_service_instantiation():
    svc = ProjectAnalysisService()
    assert svc is not None
