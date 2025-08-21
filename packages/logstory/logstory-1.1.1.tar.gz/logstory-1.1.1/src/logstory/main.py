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
"""Logstory Events replay."""

import datetime
import json
import os
import re
from pathlib import Path
from typing import Any, Protocol

import yaml
from google.auth.transport import requests
from google.cloud import secretmanager, storage
from google.oauth2 import service_account

# Import the new abstraction modules
try:
  from .auth import (
      create_auth_handler,
      detect_auth_type,
      has_application_default_credentials,
  )
  from .ingestion import IngestionBackend, create_ingestion_backend
except ImportError:
  # Fallback for when running as main module
  from auth import (  # type: ignore[import-not-found,no-redef]
      create_auth_handler,
      detect_auth_type,
      has_application_default_credentials,
  )
  from ingestion import (  # type: ignore[import-not-found,no-redef]
      IngestionBackend,
      create_ingestion_backend,
  )


# Type for match-like objects
class MatchLike(Protocol):
  """Protocol for objects that behave like regex matches."""

  def start(self) -> int:
    ...

  def end(self) -> int:
    ...

  def group(self, n: int = 0) -> str:
    ...


# Constants
DEFAULT_YEAR_FOR_INCOMPLETE_TIMESTAMPS = 1900
BATCH_SIZE_THRESHOLD = 1000
BATCH_BYTES_THRESHOLD = 500_000
# Windows epoch (Jan 1, 1601) in Unix epoch (Jan 1, 1970) seconds
# This is the difference in 100-nanosecond intervals between the two epochs.
EPOCH_AS_FILETIME = 116444736000000000
# Number of 100-nanosecond intervals in one second
HUNDREDS_OF_NANOSECONDS = 10000000

level = os.environ.get("PYTHONLOGLEVEL", "INFO").upper()
try:  # main.py shouldn't need abseil
  # pylint: disable-next=g-import-not-at-top
  from absl import logging

  absl_log_levels = {
      "DEBUG": logging.DEBUG,
      "INFO": logging.INFO,
      "WARNING": logging.WARNING,
      "ERROR": logging.ERROR,
      "FATAL": logging.FATAL,
  }
  logging.set_verbosity(absl_log_levels.get(level, logging.INFO))
  LOGGER = logging
except ImportError:  # set up logging without abseil
  # pylint: disable-next=g-import-not-at-top
  import logging

  logging.basicConfig(level=getattr(logging, level, logging.INFO))
  logging.getLogger().setLevel(getattr(logging, level, logging.INFO))
  LOGGER = logging.getLogger(__name__)


# Constants common to all cloud functions
SCOPES = ["https://www.googleapis.com/auth/malachite-ingestion"]
SECRET_MANAGER_CREDENTIALS = os.environ.get("SECRET_MANAGER_CREDENTIALS")
CUSTOMER_ID = os.environ.get("CUSTOMER_ID")
CREDENTIALS_PATH = os.environ.get("CREDENTIALS_PATH")
CREDENTIALS_JSON = os.environ.get("LOGSTORY_CREDENTIALS")

REGION = os.environ.get("REGION")
url_prefix = f"{REGION}-" if REGION else ""
if url_prefix.lower().strip() == "us-":  # Region US is blank rather than "us-"
  url_prefix = ""

INGESTION_API_BASE_URL = (
    os.environ.get("INGESTION_API_BASE_URL")
    or f"https://{url_prefix}malachiteingestion-pa.googleapis.com"
)
# varies by cloud function
BUCKET_NAME = os.environ.get("BUCKET_NAME")
UTC = datetime.UTC

# New configuration for REST API
PROJECT_ID = os.environ.get("LOGSTORY_PROJECT_ID")
FORWARDER_NAME = os.environ.get("LOGSTORY_FORWARDER_NAME")
IMPERSONATE_SERVICE_ACCOUNT = os.environ.get("LOGSTORY_IMPERSONATE_SERVICE_ACCOUNT")

# Global variables for backend and client
storage_client = None
http_client = None  # Will be set based on API type

# Initialize storage client if running in cloud function
if os.getenv("SECRET_MANAGER_CREDENTIALS"):  # Running in a cloud function
  secretmanager_client = secretmanager.SecretManagerServiceClient()
  storage_client = storage.Client()
  sec_request = {"name": f"{SECRET_MANAGER_CREDENTIALS}/versions/latest"}
  sec_response = secretmanager_client.access_secret_version(sec_request)
  ret = sec_response.payload.data.decode("UTF-8")
  service_account_info = json.loads(ret)
elif CREDENTIALS_JSON:  # Credentials provided as JSON string
  service_account_info = json.loads(CREDENTIALS_JSON)
elif CREDENTIALS_PATH:  # Running locally with credentials file
  with open(CREDENTIALS_PATH) as f:
    service_account_info = json.load(f)
else:
  service_account_info = None


# Check if we can use ADC with impersonation for REST API
def can_use_application_default_credentials():
  try:
    api_type = detect_auth_type()
    return (
        has_application_default_credentials()
        and IMPERSONATE_SERVICE_ACCOUNT
        and api_type == "rest"
    )
  except ValueError:
    return False


can_use_adc = can_use_application_default_credentials()

# Initialize ingestion_backend as None by default
ingestion_backend = None

# Create authentication and backend based on API type
if (
    service_account_info
    or CREDENTIALS_PATH
    or CREDENTIALS_JSON
    or SECRET_MANAGER_CREDENTIALS
    or can_use_adc
):
  # Get API type from environment variable
  api_type = detect_auth_type()

  LOGGER.info("Using API type: %s", api_type)
  LOGGER.info("PROJECT_ID env var: %s", PROJECT_ID)

  # Create appropriate auth handler
  auth_handler = create_auth_handler(
      api_type=api_type,
      credentials_path=CREDENTIALS_PATH,
      service_account_info=service_account_info,
      secret_manager_credentials=SECRET_MANAGER_CREDENTIALS,
      impersonate_service_account=IMPERSONATE_SERVICE_ACCOUNT,
  )

  # Get HTTP client from auth handler
  http_client = auth_handler.get_http_client()

  # Create ingestion backend if we have customer ID
  if CUSTOMER_ID:
    ingestion_backend = create_ingestion_backend(
        auth_handler=auth_handler,
        customer_id=CUSTOMER_ID,
        api_type=api_type,
        project_id=PROJECT_ID,
        region=REGION,
        forwarder_name=FORWARDER_NAME,
    )
# Legacy fallback for backward compatibility when no auth is configured
elif service_account_info:
  credentials = service_account.Credentials.from_service_account_info(
      service_account_info, scopes=SCOPES
  )
  http_client = requests.AuthorizedSession(credentials)


def filetime_to_datetime(filetime):
  """Converts a Windows File Time to a Python datetime object.

  Win File Time is a 64-bit integer representing 100-nanosecond intervals
  since Jan 1, 1601 UTC.
  """
  # Calculate seconds since Unix epoch
  seconds_since_unix_epoch = (filetime - EPOCH_AS_FILETIME) / HUNDREDS_OF_NANOSECONDS
  # Create datetime object from Unix timestamp (UTC)
  return datetime.datetime.fromtimestamp(seconds_since_unix_epoch, UTC)


def datetime_to_filetime(dt):
  """Converts a Python datetime object to a Windows File Time.

  Win File Time is a 64-bit integer representing 100-nanosecond intervals
  since Jan 1, 1601 UTC.
  """
  # Convert datetime to Unix timestamp (seconds since Jan 1, 1970 UTC)
  unix_timestamp = dt.timestamp()
  # Convert to 100-nanosecond intervals and add Windows epoch offset
  return int(unix_timestamp * HUNDREDS_OF_NANOSECONDS + EPOCH_AS_FILETIME)


def _get_timestamp_delta_dict(timestamp_delta: str) -> dict[str, int]:
  """Parses the timestamp delta string into a dictionary."""
  ts_delta_pairs = re.findall(r"(\d+)([dhm])", timestamp_delta)
  return {letter: int(number) for number, letter in ts_delta_pairs}


def _validate_timestamp_config(log_type: str, timestamp_map: dict[str, Any]) -> None:
  """Validates timestamp configuration for logical consistency.

  Args:
    log_type: The log type name for error reporting.
    timestamp_map: The loaded timestamp configuration.

  Raises:
    ValueError: If the configuration is invalid or inconsistent.
  """
  if log_type not in timestamp_map:
    raise ValueError(f"Log type '{log_type}' not found in timestamp configuration")

  entry_data = timestamp_map[log_type]

  if "timestamps" not in entry_data:
    raise ValueError(f"Log type '{log_type}' missing 'timestamps' configuration")

  timestamps = entry_data["timestamps"]
  base_time_count = 0

  for i, timestamp in enumerate(timestamps):
    # Check for required fields
    required_fields = ["name", "pattern", "group", "dateformat"]
    for field in required_fields:
      if field not in timestamp:
        raise ValueError(
            f"Log type '{log_type}' timestamp {i} missing required field: '{field}'"
        )

    # Check base_time count
    if timestamp.get("base_time"):
      base_time_count += 1

    # Validate dateformat
    dateformat = timestamp.get("dateformat")

    # Dateformat must be one of the three valid types:
    # 1. 'epoch' - for Unix epoch timestamps
    # 2. 'windowsfiletime' - for Windows FileTime format
    # 3. A strftime format string (e.g., "%Y-%m-%d %H:%M:%S")

    if not dateformat:
      raise ValueError(
          f"Log type '{log_type}' timestamp {i} ({timestamp['name']}): "
          "missing required 'dateformat' field"
      )

    # Check field types
    if not isinstance(timestamp.get("name"), str):
      raise ValueError(f"Log type '{log_type}' timestamp {i}: 'name' must be string")
    if not isinstance(timestamp.get("pattern"), str):
      raise ValueError(f"Log type '{log_type}' timestamp {i}: 'pattern' must be string")
    if not isinstance(timestamp.get("dateformat"), str):
      raise ValueError(
          f"Log type '{log_type}' timestamp {i}: 'dateformat' must be string"
      )
    if not isinstance(timestamp.get("group"), int) or timestamp.get("group") < 1:
      raise ValueError(
          f"Log type '{log_type}' timestamp {i}: 'group' must be positive integer"
      )

  # Check base_time count
  if base_time_count == 0:
    raise ValueError(f"Log type '{log_type}' has no base_time: true timestamp")
  if base_time_count > 1:
    raise ValueError(
        f"Log type '{log_type}' has multiple base_time: true timestamps"
        f" ({base_time_count})"
    )

  LOGGER.debug("Timestamp configuration validation passed for log type '%s'", log_type)


def _get_log_content(
    use_case: str, log_type: str, entities: bool | None = False
) -> str:
  """Retrieves log content from either GCS or local filesystem."""
  if entities:
    object_name = f"{use_case}/ENTITIES/{log_type}.log"
  else:
    object_name = f"{use_case}/EVENTS/{log_type}.log"

  LOGGER.info("Processing file: %s", object_name)
  if storage_client:  # running in cloud function
    bucket = storage_client.bucket(BUCKET_NAME)
    file_object = bucket.get_blob(object_name)
    return file_object.download_as_text()
  # Local filesystem case
  script_dir = os.path.dirname(os.path.abspath(__file__))
  local_file_path = os.path.join(script_dir, "usecases/", object_name)
  with open(local_file_path) as f:
    return f.read()


def _get_ingestion_labels(
    use_case: str,
    logstory_exe_time: datetime.datetime,
    api_for_log_type: str,
) -> list[dict[str, Any]]:
  """Constructs the ingestion labels list."""
  return [
      {
          "key": "ingestion_method",
          "value": api_for_log_type,
      },
      {
          "key": "replayed_from",
          "value": "logstory",
      },
      {
          "key": "source_usecase",
          "value": use_case,
      },
      {
          "key": "log_replay",
          "value": "true",
      },
      {
          "key": "log_replay_time",
          # changes for each logtype in each usecase
          "value": _get_current_time().isoformat(),
      },
      {
          "key": "logstory_exe_time",
          # same value for all logtypes in all usecases. i.e. 1 value per run.
          "value": logstory_exe_time.isoformat(),
      },
  ]


def _get_current_time():
  """Returns the current time in UTC."""
  return datetime.datetime.now(UTC)


def _calculate_timestamp_replacement(
    log_text: str,
    timestamp: dict[str, str],
    old_base_time: datetime.datetime,
    ts_delta_dict: dict[str, int],
) -> tuple[MatchLike, str] | None:
  """Calculates the replacement for a timestamp without modifying the text.

  Args:
    log_text: string containing timestamp and other text
    timestamp: describes the timestamp pattern to search for
    old_base_time: the first ts in the first line of the first logfile
    ts_delta_dict: user configured offset from current datetime
      the updated timestamp will be now() - [Nd]days -[Nh]hours - [Nm]mins
      ex. 2024-03-14T13:37:42.123456Z and {d: 1, h: 1, m: 1} ->
          2024-03-13T12:36:42.123456Z
      Note that the seconds and milliseconds are always preserved.

  Returns:
    Tuple of (match object, replacement string) or None if no match
  """
  ts_match = re.search(timestamp["pattern"], log_text)
  if ts_match:
    # Get the specific group we're updating
    event_timestamp = ts_match.group(timestamp["group"])
    event_time = None
    is_filetime = False
    is_epoch = False

    dateformat = timestamp.get("dateformat")

    if dateformat == "epoch":
      # Unix epoch timestamp
      is_epoch = True
      event_time = datetime.datetime.fromtimestamp(int(event_timestamp))
    elif dateformat == "windowsfiletime":
      # Special handling for Windows FileTime
      is_filetime = True
      event_time = filetime_to_datetime(int(event_timestamp))
    else:
      # Standard strptime format
      event_time = datetime.datetime.strptime(event_timestamp, dateformat)

    if event_time:
      # `old_base_time` is the base t (bts) in the first line of the
      #  first logfile of the usecase's set of logfiles.
      # If the current timestamp has a different date from the old_base_time
      #  we want the same N days different to be in the final ts

      if event_time.year == DEFAULT_YEAR_FOR_INCOMPLETE_TIMESTAMPS:
        event_time = event_time.replace(year=old_base_time.year)
      more_days = (event_time.date() - old_base_time.date()).days
      # Get today's date minus N days
      subtract_n_days = ts_delta_dict.get("d", 0) - more_days
      new_day = _get_current_time() - datetime.timedelta(days=subtract_n_days)
      # Update date but keep the original time
      new_event_time = event_time.replace(
          year=new_day.year,
          month=new_day.month,
          day=new_day.day,
      )
      # now update the time if user provided [Nh][Nm]
      # the optional h/m delta enables running > 1x/day
      if "h" in ts_delta_dict or "m" in ts_delta_dict:
        hm_delta = datetime.timedelta(
            hours=ts_delta_dict.get("h", 0),
            minutes=ts_delta_dict.get("m", 0),
        )
        new_event_time = new_event_time - hm_delta

      # Format the new timestamp appropriately
      if is_filetime:
        # Convert back to Windows FileTime
        new_event_timestamp = str(datetime_to_filetime(new_event_time))
      elif is_epoch:
        # Convert back to Unix epoch
        new_event_timestamp = str(int(new_event_time.timestamp()))
      else:
        # Use strftime with the dateformat
        new_event_timestamp = new_event_time.strftime(dateformat)

      # Return a match object that represents ONLY the group we're changing
      # Create a GroupMatch object that has the start/end of the specific group
      class GroupMatch:

        def __init__(self, match, group_num):
          self.match = match
          self.group_num = group_num

        def start(self):
          return self.match.start(self.group_num)

        def end(self):
          return self.match.end(self.group_num)

        def group(self, n=0):
          if n == 0:
            return self.match.group(self.group_num)
          return self.match.group(self.group_num)

      return (GroupMatch(ts_match, timestamp["group"]), new_event_timestamp)
  return None


def _write_entries_to_local_file(
    log_type: str,
    all_entries: list[dict[str, str]],
    log_dir: str | None = None,
) -> None:
  """Write entries to local log files instead of sending to API.

  Args:
    log_type: The log type name for the filename
    all_entries: List of log entries to write
    log_dir: Directory to write log files to (defaults to /tmp/var/log/logstory)
  """
  # Get log directory from environment or use default
  if log_dir is None:
    log_dir = os.getenv("LOGSTORY_LOCAL_LOG_DIR", "/tmp/var/log/logstory")  # nosec B108

  # Create directory if it doesn't exist
  log_path = Path(log_dir)
  try:
    log_path.mkdir(parents=True, exist_ok=True)
  except PermissionError:
    LOGGER.error("Permission denied creating directory: %s", log_path)
    raise
  except Exception as e:
    LOGGER.error("Error creating directory %s: %s", log_path, e)
    raise

  # Write or overwrite entries to log file
  log_file_path = log_path / f"{log_type}.log"
  try:
    with open(log_file_path, "w", encoding="utf-8") as f:
      for entry in all_entries:
        try:
          # Handle different entry types
          if isinstance(entry, dict) and "logText" in entry:
            # unstructuredlogentries format
            f.write(entry["logText"] + "\n")
          elif isinstance(entry, dict):
            # udmevents/entities format - write as JSON
            f.write(json.dumps(entry) + "\n")
          else:
            # fallback for other formats
            f.write(str(entry) + "\n")
        except Exception as e:
          LOGGER.error("Error writing entry to %s: %s", log_file_path, e)
          continue

    LOGGER.info("Successfully wrote %d entries to %s", len(all_entries), log_file_path)

  except PermissionError:
    LOGGER.error("Permission denied writing to file: %s", log_file_path)
    raise
  except Exception as e:
    LOGGER.error("Error writing to file %s: %s", log_file_path, e)
    raise


def _post_entries_in_batches(
    api: str,
    log_type: str,
    all_entries: list[dict[str, str]],
    ingestion_labels: list[dict[str, str]],
    backend: IngestionBackend | None = None,
    local_file_output: bool = False,
    log_dir: str | None = None,
):
  """Posts entries to the ingestion API in batches or writes to local files."""
  # If local file output is enabled, write all entries to file and return
  if local_file_output:
    _write_entries_to_local_file(log_type, all_entries, log_dir)
    return

  # Check that backend is provided for API posting
  if not backend:
    raise RuntimeError("Backend must be provided when not using local file output")

  # Original API posting logic
  entries_bytes = 0
  entries = []
  for i, entry in enumerate(all_entries):
    entries.append(entry)
    try:
      entries_bytes += len(entry["logText"])  # unstructuredlogentry
    except (TypeError, KeyError):
      entries_bytes += len(entry)  # udmevent
    if (
        len(entries) % BATCH_SIZE_THRESHOLD == 0
        or entries_bytes > BATCH_BYTES_THRESHOLD
    ):
      LOGGER.info("posting entry N: %s, entries_bytes: %s", i, entries_bytes)
      post_entries(api, log_type, entries, ingestion_labels, backend)
      entries = []
      entries_bytes = 0

  # after the loop, also submit if there are leftover entries
  if entries:
    LOGGER.info("posting remaining entries")
    post_entries(api, log_type, entries, ingestion_labels, backend)


# pylint: disable-next=g-bare-generic
def post_entries(
    api: str,
    log_type: str,
    entries: list,
    ingestion_labels: list[dict[str, Any]],
    backend: IngestionBackend,
):
  """Send the provided entries to the appropriate ingestion API method.

  Args:
    api: which ingestion API to use (unstructured or udm)
    log_type: value from yaml; unused if UDM
    entries: list of entries to send to ingestion API
    ingestion_labels: labels to attach to the ingestion
    backend: ingestion backend to use for posting
  Returns:
    None
  """
  if not backend:
    raise RuntimeError("No ingestion backend provided")

  if api == "unstructuredlogentries":
    backend.post_unstructured_logs(log_type, entries, ingestion_labels)
  elif api == "udmevents":
    backend.post_udm_events(entries, ingestion_labels)
  elif api == "entities":
    backend.post_entities(log_type, entries, ingestion_labels)
  else:
    raise ValueError(f"Unknown API type: {api}")

  LOGGER.info(
      "Successfully posted entries using %s backend",
      backend.__class__.__name__,
  )


# pylint: disable-next=missing-function-docstring
def usecase_replay_logtype(
    use_case: str,
    log_type: str,
    logstory_exe_time: datetime.datetime,
    old_base_time: datetime.datetime | None = None,
    timestamp_delta: str | None = None,
    ts_map_path: str | None = "./",
    entities: bool | None = False,
    local_file_output: bool = False,
) -> datetime.datetime | None:
  """Replays log data for a specific use case and log type.

  Args:
    use_case: value from yaml (ex. AWS, AZURE_AD, ...)
    log_type: value from yaml (ex. CS_EDR, GCP_CLOUDAUDIT, ...)
    logstory_exe_time: common to all logtypes and all usecases
    old_base_time: the first base timestamp in the first line of the first log.
    timestamp_delta: [Nd][Nh][Nm] string, for calculating the timestampdelta
     to apply to each timestamp pattern match.
    ts_map_path: disk location of the yaml files
    entities: bool for Entities (True) vs Events (False)
    local_file_output: bool to write to local files instead of API

  Returns:
    old_base_time: so that subsequent logtypes/usecases can all use the same value
  """
  timestamp_delta = timestamp_delta or "1d"
  ts_delta_dict = _get_timestamp_delta_dict(timestamp_delta)

  # Construct the full path to the YAML file
  if entities:
    file_path = os.path.join(ts_map_path, "logtypes_entities_timestamps.yaml")
  else:
    file_path = os.path.join(ts_map_path, "logtypes_events_timestamps.yaml")

  if file_path.startswith("."):
    file_path = os.path.split(__file__)[0] + "/" + file_path
  with open(file_path) as fh:
    timestamp_map = yaml.safe_load(fh)

    # Validate timestamp configuration before processing
    _validate_timestamp_config(log_type, timestamp_map)

    api_for_log_type = timestamp_map[log_type]["api"]
    # Get optional log_dir from YAML config, defaults to None for backwards compatibility
    log_type_log_dir = timestamp_map[log_type].get("log_dir")
    log_content = _get_log_content(use_case, log_type, entities)
    ingestion_labels = _get_ingestion_labels(
        use_case, logstory_exe_time, api_for_log_type
    )
    # base time stamp (BTS) determines the anchor point; others are relative
    btspattern, btsgroup, btsformat = [
        (
            timestamp.get("pattern"),
            timestamp.get("group"),
            timestamp.get("dateformat"),
        )
        for timestamp in timestamp_map[log_type]["timestamps"]
        if timestamp.get("base_time")
    ][0]

    # First pass: Find all base_time timestamps and get the maximum
    if old_base_time is None:
      base_timestamps = []
      for log_text in log_content.splitlines():
        match = re.search(btspattern, log_text)
        if match and match.groups():
          timestamp_str = match.group(btsgroup)
          try:
            if btsformat == "epoch":
              # Unix epoch timestamp
              dt = datetime.datetime.fromtimestamp(int(timestamp_str))
            elif btsformat == "windowsfiletime":
              # Windows FileTime
              dt = filetime_to_datetime(int(timestamp_str))
            else:
              # Standard strptime format
              dt = datetime.datetime.strptime(timestamp_str, btsformat)
            base_timestamps.append(dt)
          except (ValueError, OverflowError) as e:
            LOGGER.warning("Failed to parse base timestamp '%s': %s", timestamp_str, e)
            continue

      if base_timestamps:
        old_base_time = max(base_timestamps)
        LOGGER.debug(
            "Selected maximum base_time from %d timestamps: %s",
            len(base_timestamps),
            old_base_time,
        )
      else:
        LOGGER.error("No valid base_time timestamps found in log file")

    # Second pass: Process log entries
    entries = []
    for line_no, log_text in enumerate(log_content.splitlines()):

      # Collect all timestamp replacements for this line using a change map
      # This prevents double-updates and handles overlapping patterns intelligently
      change_map: dict[tuple[int, int, str], str] = (
          {}
      )  # (start, end, original_text) -> replacement_text

      for ts_n, timestamp in enumerate(timestamp_map[log_type]["timestamps"]):
        replacement_info = _calculate_timestamp_replacement(
            log_text,
            timestamp,
            old_base_time,
            ts_delta_dict,
        )
        if replacement_info:
          match, replacement = replacement_info
          change_key = (match.start(), match.end(), match.group(0))

          if change_key in change_map:
            # Check if it's the same change or a conflict
            if change_map[change_key] != replacement:
              LOGGER.warning(
                  "Timestamp replacement conflict at position %d-%d: '%s' -> '%s' vs"
                  " '%s'",
                  match.start(),
                  match.end(),
                  match.group(0),
                  change_map[change_key],
                  replacement,
              )
            # else: Same change, no-op
          else:
            change_map[change_key] = replacement

        LOGGER.debug("Finished processing line N: %s, timestamp N: %s", line_no, ts_n)

      # Apply all unique replacements in reverse order to preserve positions
      for (start, end, _), replacement in sorted(
          change_map.items(), key=lambda x: x[0][0], reverse=True
      ):
        log_text = log_text[:start] + replacement + log_text[end:]

      # accumulate all of the entries into memory
      LOGGER.debug("log_text after all ts updates: %s", log_text)
      LOGGER.debug("now as repr:")
      LOGGER.debug(repr(log_text))
      if api_for_log_type == "unstructuredlogentries":
        entries.append({"logText": log_text})
      elif api_for_log_type in {"udmevents", "entities"}:
        entries.append(json.loads(log_text))
      else:
        raise ValueError("Only unstructuredlogentries and udmevents are supported")

    _post_entries_in_batches(
        api_for_log_type,
        log_type,
        entries,
        ingestion_labels,
        ingestion_backend,
        local_file_output,
        log_type_log_dir,
    )
  return old_base_time


def main(request=None, enabled=False):  # pylint: disable=unused-argument
  """Read config and call usecase_replay_logtype for each [usecase, logtype].

  This is the entry point for the Cloud Function. It is not used by CLI.

  It calls usecases_replay for each of the usecases that is
   in the file usecases_events_logtype_map.yaml where: enabled: 1
  There is also log_type list in that config. That is duplicative if all of
   the log types in the subdir are used but it is useful to be able to toggle
   some off.

  old_base_time is the first base timestamp in the first line of the first log.
   - all changes are relative to that value: both interlog and intraline.
   - if line N of log N is > than old_base_time, the event_time will be in the future.
   - if it is > 30 days in the future, it will be 9999-01-01

  NOTE: this fx is not used by logstory.py, so local filenames are ok

  Args:
   request: Unused; Needed for running in Cloud Function.
   enabled: Flag to force running all usecases.

  Returns:
   Success Events!
  """
  logstory_exe_time = _get_current_time()
  entities = os.getenv("ENTITIES")
  if entities:
    filename = "usecases_entities_logtype_map.yaml"
  else:
    filename = "usecases_events_logtype_map.yaml"

  with open(os.path.join(os.path.dirname(__file__), filename)) as fh:
    yaml_use_cases = yaml.safe_load(fh)
    use_cases = list(yaml_use_cases.keys())
    for use_case in use_cases:
      if (yaml_use_cases[use_case]["enabled"]) > 0 or enabled:
        LOGGER.info("use_case: %s", use_case)
        old_base_time = None  # reset for each usecase
        for log_type in yaml_use_cases[use_case]["log_type"]:
          old_base_time = None  # reset for each log_type
          LOGGER.info("log_type: %s", log_type)
          old_base_time = usecase_replay_logtype(
              use_case,
              log_type,
              logstory_exe_time,
              old_base_time,
              timestamp_delta="1d",
              entities=entities,  # bool
          )
    LOGGER.info("use_case: %s completed.", use_case)
    LOGGER.info(
        "UDM Search for the loaded logs:\n"
        "    metadata.ingested_timestamp.seconds >= %s\n"
        "    metadata.log_type = %s\n"
        '    metadata.ingestion_labels["replayed_from"] = "logstory"\n'
        '    metadata.ingestion_labels["log_replay"] = "true"\n'
        '    metadata.ingestion_labels["source_usecase"] = "%s"',
        int(logstory_exe_time.timestamp()),
        log_type,
        use_case,
    )
  return "Success Events!"
