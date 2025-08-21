# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Authentication abstraction for Logstory to support multiple ingestion APIs."""

import json
import os
from abc import ABC, abstractmethod
from typing import Any

import google.auth
from google.auth import impersonated_credentials
from google.auth.credentials import Credentials
from google.auth.exceptions import DefaultCredentialsError
from google.auth.transport import requests
from google.oauth2 import service_account


def validate_credentials_match_api_type(
    api_type: str,
    service_account_info: dict[str, Any] | None = None,
    credentials_path: str | None = None,
) -> None:
  """Validate that credentials match the specified API type.

  Args:
    api_type: "legacy" or "rest"
    service_account_info: Service account JSON as dictionary
    credentials_path: Path to service account JSON file

  Raises:
    ValueError: If credentials don't match the API type
  """
  # Get the service account info from either source
  info = None
  if service_account_info:
    info = service_account_info
  elif credentials_path:
    try:
      with open(credentials_path) as f:
        info = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
      # If we can't read the file, let the auth handler deal with it
      return

  if not info:
    return

  # Check if client_email exists
  client_email = info.get("client_email", "")
  if not client_email:
    return

  # Check for malachite pattern in email
  is_malachite_credential = "@malachite-" in client_email

  # Validate based on API type
  if api_type == "rest" and is_malachite_credential:
    raise ValueError(
        "Invalid credentials for REST API: Found legacy malachite credentials "
        f"(client_email: {client_email}). "
        "REST API requires standard service account credentials with "
        "'cloud-platform' scope. Please use the correct credentials for the REST API."
    )

  if api_type == "legacy" and not is_malachite_credential:
    # This is a warning case - might still work but not typical
    import warnings

    warnings.warn(
        "Using non-malachite credentials with legacy API "
        f"(client_email: {client_email}). "
        "Legacy API typically uses malachite credentials. "
        "Ensure your credentials have 'malachite-ingestion' scope.",
        UserWarning,
        stacklevel=2,
    )


class AuthHandler(ABC):
  """Abstract base class for authentication handlers."""

  @abstractmethod
  def get_credentials(self) -> Credentials:
    """Get authenticated credentials for API calls."""

  @abstractmethod
  def get_http_client(self) -> requests.AuthorizedSession:
    """Get an HTTP client with authentication headers."""

  @abstractmethod
  def get_scopes(self) -> list[str]:
    """Get the OAuth scopes required for this authentication method."""


class LegacyAuthHandler(AuthHandler):
  """Authentication handler for the legacy malachite ingestion API."""

  SCOPES = ["https://www.googleapis.com/auth/malachite-ingestion"]

  def __init__(
      self,
      service_account_info: dict[str, Any] | None = None,
      credentials_path: str | None = None,
      secret_manager_credentials: str | None = None,
  ):
    """Initialize legacy authentication handler.

    Args:
      service_account_info: Service account JSON as dictionary
      credentials_path: Path to service account JSON file
      secret_manager_credentials: Secret Manager path for credentials
    """
    self.service_account_info = service_account_info
    self.credentials_path = credentials_path
    self.secret_manager_credentials = secret_manager_credentials
    self._credentials = None
    self._http_client = None

  def get_scopes(self) -> list[str]:
    """Get the OAuth scopes for legacy API."""
    return self.SCOPES

  def get_credentials(self) -> Credentials:
    """Get credentials for the legacy API."""
    if self._credentials:
      return self._credentials

    # Priority: service_account_info > credentials_path > secret_manager
    if self.service_account_info:
      self._credentials = service_account.Credentials.from_service_account_info(
          self.service_account_info, scopes=self.SCOPES
      )
    elif self.credentials_path:
      with open(self.credentials_path) as f:
        info = json.load(f)
      self._credentials = service_account.Credentials.from_service_account_info(
          info, scopes=self.SCOPES
      )
    elif self.secret_manager_credentials:
      # Import here to avoid dependency if not using Secret Manager
      from google.cloud import secretmanager

      client = secretmanager.SecretManagerServiceClient()
      request = {"name": f"{self.secret_manager_credentials}/versions/latest"}
      response = client.access_secret_version(request)
      info = json.loads(response.payload.data.decode("UTF-8"))
      self._credentials = service_account.Credentials.from_service_account_info(
          info, scopes=self.SCOPES
      )
    else:
      raise ValueError(
          "No credentials provided. Please provide service_account_info, "
          "credentials_path, or secret_manager_credentials."
      )

    return self._credentials

  def get_http_client(self) -> requests.AuthorizedSession:
    """Get an authorized HTTP session for the legacy API."""
    if not self._http_client:
      self._http_client = requests.AuthorizedSession(self.get_credentials())
    return self._http_client


class RestAuthHandler(AuthHandler):
  """Authentication handler for the new Chronicle REST API."""

  SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

  def __init__(
      self,
      service_account_info: dict[str, Any] | None = None,
      credentials_path: str | None = None,
      impersonate_service_account: str | None = None,
  ):
    """Initialize REST API authentication handler.

    Args:
      service_account_info: Service account JSON as dictionary
      credentials_path: Path to service account JSON file
      impersonate_service_account: Email of service account to impersonate
    """
    self.service_account_info = service_account_info
    self.credentials_path = credentials_path
    self.impersonate_service_account = impersonate_service_account
    self._credentials = None
    self._http_client = None

  def get_scopes(self) -> list[str]:
    """Get the OAuth scopes for REST API."""
    return self.SCOPES

  def get_credentials(self) -> Credentials:
    """Get credentials for the REST API."""
    if self._credentials:
      return self._credentials

    # Get base credentials
    if self.service_account_info:
      base_credentials = service_account.Credentials.from_service_account_info(
          self.service_account_info, scopes=self.SCOPES
      )
    elif self.credentials_path:
      base_credentials = service_account.Credentials.from_service_account_file(
          self.credentials_path, scopes=self.SCOPES
      )
    else:
      # Try Application Default Credentials
      import google.auth

      base_credentials, _ = google.auth.default(scopes=self.SCOPES)

    # Handle impersonation if requested
    if self.impersonate_service_account:
      self._credentials = impersonated_credentials.Credentials(
          source_credentials=base_credentials,
          target_principal=self.impersonate_service_account,
          target_scopes=self.SCOPES,
          lifetime=600,
      )
    else:
      self._credentials = base_credentials

    return self._credentials

  def get_http_client(self) -> requests.AuthorizedSession:
    """Get an authorized HTTP session for the REST API."""
    if not self._http_client:
      session = requests.AuthorizedSession(self.get_credentials())
      # Add custom user agent for tracking
      session.headers["User-Agent"] = "logstory-rest-api"
      self._http_client = session
    return self._http_client


def has_application_default_credentials() -> bool:
  """Check if Application Default Credentials are available.

  Returns:
    True if ADC are available, False otherwise.
  """
  try:
    # Try to load ADC without actually using them
    credentials, _ = google.auth.default()
    return credentials is not None
  except DefaultCredentialsError:
    return False
  except Exception:
    # Any other error means ADC is not available
    return False


def detect_auth_type() -> str:
  """Get API type from LOGSTORY_API_TYPE environment variable.

  Returns:
    Value of LOGSTORY_API_TYPE environment variable

  Raises:
    ValueError: If LOGSTORY_API_TYPE is not set or invalid
  """
  api_type = os.environ.get("LOGSTORY_API_TYPE")
  if not api_type:
    raise ValueError(
        "LOGSTORY_API_TYPE environment variable must be set to 'rest' or 'legacy'"
    )

  api_type = api_type.lower()
  if api_type not in ["rest", "legacy"]:
    raise ValueError(
        f"Invalid LOGSTORY_API_TYPE='{api_type}'. Must be 'rest' or 'legacy'"
    )

  return api_type


def create_auth_handler(
    api_type: str | None = None,
    credentials_path: str | None = None,
    service_account_info: dict[str, Any] | None = None,
    secret_manager_credentials: str | None = None,
    impersonate_service_account: str | None = None,
) -> AuthHandler:
  """Factory function to create the appropriate auth handler.

  Args:
    api_type: "legacy" or "rest" (auto-detect if None)
    credentials_path: Path to service account JSON file
    service_account_info: Service account JSON as dictionary
    secret_manager_credentials: Secret Manager path (legacy only)
    impersonate_service_account: Service account to impersonate (REST only)

  Returns:
    AuthHandler instance for the selected API type
  """
  # Auto-detect if not specified
  if not api_type:
    api_type = detect_auth_type()

  # Validate credentials match the API type
  validate_credentials_match_api_type(
      api_type,
      service_account_info=service_account_info,
      credentials_path=credentials_path,
  )

  if api_type == "rest":
    if secret_manager_credentials:
      raise ValueError(
          "Secret Manager credentials are not supported with REST API. "
          "Please use credentials_path or service_account_info."
      )
    return RestAuthHandler(
        service_account_info=service_account_info,
        credentials_path=credentials_path,
        impersonate_service_account=impersonate_service_account,
    )
  if api_type == "legacy":
    if impersonate_service_account:
      raise ValueError(
          "Service account impersonation is not supported with legacy API. "
          "Please use the REST API for impersonation support."
      )
    return LegacyAuthHandler(
        service_account_info=service_account_info,
        credentials_path=credentials_path,
        secret_manager_credentials=secret_manager_credentials,
    )
  raise ValueError(f"Unknown API type: {api_type}. Use 'legacy' or 'rest'.")
