from uuid import uuid4

import pytest

from .client import orca_api
from .credentials import OrcaCredentials


def test_list_api_keys():
    api_keys = OrcaCredentials.list_api_keys()
    assert len(api_keys) >= 1
    assert "orca_sdk_test" in [api_key.name for api_key in api_keys]


def test_list_api_keys_unauthenticated(unauthenticated):
    with pytest.raises(ValueError, match="Invalid API key"):
        OrcaCredentials.list_api_keys()


def test_is_authenticated():
    assert OrcaCredentials.is_authenticated()


def test_is_authenticated_false(unauthenticated):
    assert not OrcaCredentials.is_authenticated()


def test_set_api_key(api_key, unauthenticated):
    assert not OrcaCredentials.is_authenticated()
    OrcaCredentials.set_api_key(api_key)
    assert OrcaCredentials.is_authenticated()


def test_set_invalid_api_key(api_key):
    assert OrcaCredentials.is_authenticated()
    with pytest.raises(ValueError, match="Invalid API key"):
        OrcaCredentials.set_api_key(str(uuid4()))
    assert not OrcaCredentials.is_authenticated()


def test_set_base_url(base_url_reset):
    OrcaCredentials.set_base_url("http://api.orcadb.ai")
    assert str(orca_api.base_url) == "http://api.orcadb.ai"


def test_set_invalid_base_url():
    with pytest.raises(ValueError, match="No API found at http://localhost:1582"):
        OrcaCredentials.set_base_url("http://localhost:1582")


def test_is_healthy():
    assert OrcaCredentials.is_healthy()


def test_is_healthy_false(base_url_reset):
    OrcaCredentials.set_base_url("http://localhost:1582", check_validity=False)
    assert not OrcaCredentials.is_healthy()
