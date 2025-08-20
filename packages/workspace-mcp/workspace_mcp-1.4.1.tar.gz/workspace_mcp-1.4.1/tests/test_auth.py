import os
import json
from unittest.mock import patch
import pytest
from auth.google_auth import load_client_secrets_from_env, create_oauth_flow, load_client_secrets

# -- Mocks and Fixtures --

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to mock environment variables for OAuth."""
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "test_client_id_from_env")
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "test_client_secret_from_env")
    monkeypatch.setenv("GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:8000/callback")
    return monkeypatch

@pytest.fixture
def mock_client_secrets_file(tmp_path):
    """Fixture to create a mock client_secret.json file."""
    secrets_content = {
        "web": {
            "client_id": "test_client_id_from_file",
            "client_secret": "test_client_secret_from_file",
            "redirect_uris": ["http://localhost:8000/oauth2callback"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }
    secrets_file = tmp_path / "client_secret.json"
    secrets_file.write_text(json.dumps(secrets_content))
    return str(secrets_file)

# -- Tests for load_client_secrets_from_env --

def test_load_client_secrets_from_env_success(mock_env_vars):
    """Test loading client secrets from environment variables successfully."""
    config = load_client_secrets_from_env()
    assert config is not None
    assert config["web"]["client_id"] == "test_client_id_from_env"
    assert config["web"]["client_secret"] == "test_client_secret_from_env"
    assert config["web"]["redirect_uris"] == ["http://localhost:8000/callback"]

def test_load_client_secrets_from_env_missing_vars():
    """Test that None is returned when environment variables are missing."""
    # Ensure variables are not set
    if "GOOGLE_OAUTH_CLIENT_ID" in os.environ:
        del os.environ["GOOGLE_OAUTH_CLIENT_ID"]
    config = load_client_secrets_from_env()
    assert config is None

# -- Tests for load_client_secrets (the combined function) --

def test_load_client_secrets_prioritizes_env_vars(mock_env_vars, mock_client_secrets_file):
    """Test that environment variables are prioritized over the file."""
    # Pass a file path, but env vars should be used
    config = load_client_secrets(mock_client_secrets_file)
    assert config["client_id"] == "test_client_id_from_env"
    assert config["client_secret"] == "test_client_secret_from_env"

def test_load_client_secrets_falls_back_to_file(mock_client_secrets_file):
    """Test that the file is used when no environment variables are set."""
    # Ensure env vars are not present
    if "GOOGLE_OAUTH_CLIENT_ID" in os.environ:
        del os.environ["GOOGLE_OAUTH_CLIENT_ID"]

    config = load_client_secrets(mock_client_secrets_file)
    assert config["client_id"] == "test_client_id_from_file"
    assert config["client_secret"] == "test_client_secret_from_file"

def test_load_client_secrets_file_not_found():
    """Test that an error is raised if no file is found and no env vars are set."""
    with pytest.raises(IOError):
        load_client_secrets("non_existent_file.json")

# -- Tests for create_oauth_flow --

@patch('auth.google_auth.Flow')
def test_create_oauth_flow_from_env(mock_flow, mock_env_vars):
    """Test creating an OAuth flow using environment variables."""
    create_oauth_flow(scopes=["test_scope"], redirect_uri="http://localhost:8000/callback")

    # Check that Flow.from_client_config was called with the correct config
    mock_flow.from_client_config.assert_called_once()
    call_args = mock_flow.from_client_config.call_args[0][0]
    assert call_args["web"]["client_id"] == "test_client_id_from_env"

@patch('auth.google_auth.Flow')
@patch('os.path.exists', return_value=True)
def test_create_oauth_flow_from_file(mock_path_exists, mock_flow, mock_client_secrets_file):
    """Test creating an OAuth flow using a client secrets file."""
    # Ensure env vars are not present
    if "GOOGLE_OAUTH_CLIENT_ID" in os.environ:
        del os.environ["GOOGLE_OAUTH_CLIENT_ID"]

    with patch('auth.google_auth.CONFIG_CLIENT_SECRETS_PATH', mock_client_secrets_file):
        create_oauth_flow(scopes=["test_scope"], redirect_uri="http://localhost:8000/callback")

    # Check that Flow.from_client_secrets_file was called
    mock_flow.from_client_secrets_file.assert_called_once_with(
        mock_client_secrets_file,
        scopes=["test_scope"],
        redirect_uri="http://localhost:8000/callback",
        state=None
    )

@patch('os.path.exists', return_value=False)
def test_create_oauth_flow_no_config_found(mock_path_exists):
    """Test that an error is raised if no configuration is found."""
    # Ensure env vars are not present
    if "GOOGLE_OAUTH_CLIENT_ID" in os.environ:
        del os.environ["GOOGLE_OAUTH_CLIENT_ID"]

    with pytest.raises(FileNotFoundError):
        create_oauth_flow(scopes=["test_scope"], redirect_uri="http://localhost:8000/callback")