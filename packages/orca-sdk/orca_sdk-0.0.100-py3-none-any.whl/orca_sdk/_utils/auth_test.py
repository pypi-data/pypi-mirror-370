from uuid import uuid4

from ..credentials import OrcaCredentials
from .auth import _create_api_key, _delete_api_key, _delete_org, _list_api_keys


def test_list_api_keys(org_id):
    assert len(_list_api_keys(org_id)) >= 1


def test_create_api_key(org_id):
    name = f"test-{uuid4().hex[:8]}"
    api_key = _create_api_key(org_id=org_id, name=name)
    assert api_key is not None
    assert name in [api_key.name for api_key in OrcaCredentials.list_api_keys()]


def test_delete_api_key(org_id):
    name = f"test-{uuid4().hex[:8]}"
    api_key = _create_api_key(org_id=org_id, name=name)
    assert api_key is not None
    assert name in [api_key.name for api_key in OrcaCredentials.list_api_keys()]
    _delete_api_key(org_id=org_id, name=name)
    assert name not in [api_key.name for api_key in OrcaCredentials.list_api_keys()]


def test_delete_org(other_org_id):
    _create_api_key(org_id=other_org_id, name="test")
    assert len(_list_api_keys(other_org_id)) >= 1
    _delete_org(other_org_id)
    assert len(_list_api_keys(other_org_id)) == 0
