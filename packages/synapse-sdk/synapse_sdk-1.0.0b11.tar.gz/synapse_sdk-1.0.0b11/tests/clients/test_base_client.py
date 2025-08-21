import pytest
from pydantic import ValidationError

from synapse_sdk.clients.backend.models import Storage, UpdateJob
from synapse_sdk.clients.base import BaseClient


@pytest.fixture
def base_client():
    return BaseClient('http://fake_url')


@pytest.fixture
def valid_storage_response():
    return {
        'id': 1,
        'name': 'test_storage',
        'category': 'internal',
        'provider': 'file_system',
        'configuration': {},
        'is_default': True,
    }


@pytest.fixture
def invalid_storage_response(valid_storage_response):
    response = valid_storage_response.copy()
    response['provider'] = 'invalid_provider'
    return response


def test_validate_response_with_pydantic_model_success(base_client, valid_storage_response):
    validated_response = base_client._validate_response_with_pydantic_model(valid_storage_response, Storage)
    assert validated_response['id'] == valid_storage_response['id']


def test_validate_response_with_pydantic_model_invalid_data(base_client, invalid_storage_response):
    with pytest.raises(ValidationError) as exc_info:
        base_client._validate_response_with_pydantic_model(invalid_storage_response, Storage)
    assert '1 validation error' in str(exc_info.value)


def test_validate_response_with_pydantic_model_not_pydantic_model(base_client, valid_storage_response):
    with pytest.raises(TypeError) as exc_info:
        base_client._validate_response_with_pydantic_model(valid_storage_response, {})
    assert 'The provided model is not a pydantic model' in str(exc_info.value)


def test_validate_update_job_request_body_with_pydantic_model_success(base_client):
    request_body = {
        'status': 'running',
    }
    validated_request_body = base_client._validate_request_body_with_pydantic_model(
        request_body,
        UpdateJob,
    )
    assert validated_request_body['status'] == request_body['status']
