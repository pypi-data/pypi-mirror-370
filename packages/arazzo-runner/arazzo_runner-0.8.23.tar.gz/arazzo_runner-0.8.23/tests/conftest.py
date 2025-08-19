import pytest
from arazzo_runner.http import HTTPExecutor
from arazzo_runner.blob_store import InMemoryBlobStore


class MockCredentialProvider:
    """Mock credential provider for testing - ONLY mock out what we need"""

    def get_credentials(self, security_options, fetch_options):
        """Mock implementation of get_credentials"""
        return []


@pytest.fixture
def basic_http_client() -> HTTPExecutor:
    """HTTP client without auth provider for basic tests"""
    return HTTPExecutor()


@pytest.fixture  
def http_client() -> HTTPExecutor:
    """HTTP client with mock auth provider for tests"""
    return HTTPExecutor(
        auth_provider=MockCredentialProvider()
    ) 