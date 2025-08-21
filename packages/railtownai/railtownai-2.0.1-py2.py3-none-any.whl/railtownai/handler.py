"""Logging handler for the Railtown AI Python SDK."""

from __future__ import annotations

#   -------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   -------------------------------------------------------------
import datetime
import json
import logging
import traceback
from typing import Any

from .api_client import get_http_client
from .breadcrumbs import get_breadcrumbs
from .config import get_api_key, get_config
from .models import RailtownPayload


class RailtownHandler(logging.Handler):
    """Custom logging handler that sends log records to Railtown AI."""

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self._config = None

    def emit(self, record: logging.LogRecord) -> None:
        """Send the log record to Railtown AI."""
        try:
            config = self._get_config()
            if not config:
                return

            # Get breadcrumbs
            breadcrumbs = get_breadcrumbs()

            # Convert log level to string
            level_map = {
                logging.DEBUG: "debug",
                logging.INFO: "info",
                logging.WARNING: "warning",
                logging.ERROR: "error",
                logging.CRITICAL: "critical",
            }
            level_str = level_map.get(record.levelno, "info")

            # Get exception info if available
            exception_info = ""
            if record.exc_info:
                exception_info = "".join(traceback.format_exception(*record.exc_info))

            # Prepare properties from record
            properties = {}
            if hasattr(record, "extra_data"):
                if isinstance(record.extra_data, dict):
                    properties.update(record.extra_data)
                else:
                    properties["extra_data"] = record.extra_data

            # Add breadcrumbs to properties
            if breadcrumbs:
                properties["Breadcrumbs"] = breadcrumbs

            # Add any extra fields from the record
            excluded_fields = {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
                "extra_data",
            }

            for key, value in record.__dict__.items():
                if key not in excluded_fields:
                    properties[key] = value

            # Transform specific fields from snake_case to PascalCase
            properties = self._transform_property_keys(properties)

            payload = [
                {
                    "Body": str(
                        RailtownPayload(
                            Message=record.getMessage(),
                            Level=level_str,
                            Exception=exception_info,
                            OrganizationId=config["o"],
                            ProjectId=config["p"],
                            EnvironmentId=config["e"],
                            Runtime="python-traceback",
                            TimeStamp=datetime.datetime.now().isoformat(),
                            Properties=properties,
                        ).model_dump()
                    ),
                    "UserProperties": {
                        "AuthenticationCode": config["h"],
                        "ClientVersion": "Python-2.0.1",  # VERSION Must match __version__ in __init__.py
                        "Encoding": "utf-8",
                        "ConnectionName": config["u"],
                    },
                }
            ]

            http_client = get_http_client()
            http_client.post(
                "https://" + config["u"],
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "railtown-py(python)",
                },
                json_data=payload,
                timeout=10,
            )

        except Exception as e:
            # Avoid infinite recursion by not logging handler errors
            print(f"Railtown handler error: {e}")

    def _get_config(self) -> dict[str, Any] | None:
        """Get the Railtown configuration."""
        if self._config is None:
            try:
                self._config = get_config()
            except Exception:
                return None
        return self._config

    def _transform_property_keys(self, properties: dict[str, Any]) -> dict[str, Any]:
        """
        Transform property keys from snake_case to PascalCase.

        Args:
            properties: The properties dictionary to transform

        Returns:
            A new dictionary with transformed keys
        """
        # Define specific mappings for special cases
        specific_mappings = {
            "run_id": "ConductrAgentRunId",
            "session_id": "ConductrAgentSessionId",
        }

        transformed_properties = {}

        for key, value in properties.items():
            # Check if this key has a specific mapping first
            if key in specific_mappings:
                transformed_properties[specific_mappings[key]] = value
            # Convert other snake_case keys to PascalCase
            elif "_" in key:
                # Split by underscore and capitalize each word
                words = key.split("_")
                pascal_key = "".join(word.capitalize() for word in words)
                transformed_properties[pascal_key] = value
            else:
                # Keep the original key if it's not snake_case
                transformed_properties[key] = value

        return transformed_properties

    def _get_platform_api_url(self) -> str | None:
        """
        Internal method to get the platform URL from the Railtown API.
        """
        config = self._get_config()
        if not config:
            return None

        url = config["u"]

        if url.startswith("tst"):
            return "https://testcndr.railtown.ai/api"
        elif url.startswith("ovr"):
            return "https://overwatch.railtown.ai/api"
        else:
            return "https://cndr.railtown.ai/api"

    def _get_conductr_presigned_sas_url(self) -> str | None:
        """
        Internal method to get a presigned SAS URL from the Railtown API.

        Returns:
            str | None: The presigned SAS URL if successful, None otherwise
        """
        try:
            config = self._get_config()
            if not config:
                return None

            platform_api_url = self._get_platform_api_url()
            endpoint_url = f"{platform_api_url}/observe/exchange"
            railtown_api_key = get_api_key()

            # Prepare the request headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "railtown-py(python)",
                "Authorization": f"Bearer {config['h']}",
            }

            # Prepare the payload as the Railtown API key with encapsulating double quotes
            payload = f'"{railtown_api_key}"'

            # Make the request to get the presigned SAS URL
            http_client = get_http_client()
            response = http_client.post(
                endpoint_url,
                headers=headers,
                data=payload,
                timeout=10,
            )

            if response.ok:
                logging.info(f"✅ Successfully got presigned SAS URL: {response.text.strip()}")
                return response.text.strip()
            else:
                logging.error(f"Failed to get presigned SAS URL: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Error getting presigned SAS URL: {e}")
            return None

    def _upload_single_agent_run(self, data: dict[str, Any]) -> bool:
        """
        Internal method to upload a single JSON object to blob storage using a presigned SAS URL.
        Only uploads if the data contains nodes, steps, and edges with length > 0.
        Also validates that the data contains required fields: name, session_id, and run_id.

        Args:
            data: The JSON object to save

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate required fields
            required_fields = ["name", "session_id", "run_id"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                logging.error(f"Skipping upload: data missing required fields: {missing_fields}")
                return False

            # Check if data has the required fields with length > 0
            nodes = data.get("nodes", [])
            steps = data.get("steps", [])
            edges = data.get("edges", [])

            if not (len(nodes) > 0 and len(steps) > 0 and len(edges) > 0):
                logging.info("Skipping upload: data missing required fields (nodes, steps, edges) or they are empty")
                return False

            # Get the presigned SAS URL
            sas_url = self._get_conductr_presigned_sas_url()
            if not sas_url:
                logging.error("Failed to get presigned SAS URL")
                return False

            logging.info(f"upload_agent_run(): Uploading JSON data to blob: {sas_url}")
            # Convert data to JSON string
            json_data = json.dumps(data, indent=2, ensure_ascii=False)

            # Upload the JSON data to the blob storage
            http_client = get_http_client()
            response = http_client.put(
                sas_url,
                data=json_data.encode("utf-8"),
                headers={
                    "Content-Type": "text/plain; charset=utf-8",
                    "x-ms-version": "2022-11-02",
                    "x-ms-blob-type": "BlockBlob",
                },
                timeout=30,
            )

            if response.ok:
                logging.info(f"✅ Successfully saved to blob: {response.status_code}")
                return True
            else:
                logging.error(f"Failed to save to blob: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Error saving to blob: {e}")
            return False

    def upload_agent_run(self, payloads: dict[str, Any] | list[dict[str, Any]]) -> bool:
        """
        Public method to save JSON object(s) to blob storage using presigned SAS URLs.
        Accepts either a single JSON object or an array of JSON objects.
        Only uploads if each payload contains nodes, steps, and edges with length > 0.
        When an array is provided, each payload gets its own fresh SAS URL.

        Args:
            payloads: Either a single JSON object or a list of JSON objects to save

        Returns:
            bool: True if all uploads succeed, False if any upload fails
        """
        try:
            # Normalize input: if single dict, wrap in list for uniform processing
            if isinstance(payloads, dict):
                payload_list = [payloads]
            elif isinstance(payloads, list):
                payload_list = payloads
            else:
                logging.error(f"Invalid input type: {type(payloads)}. Expected dict or list of dicts.")
                return False

            # Validate that all items in the list are dictionaries
            if not all(isinstance(payload, dict) for payload in payload_list):
                logging.error("All payloads must be dictionaries")
                return False

            if not payload_list:
                logging.info("No payloads to upload")
                return True

            logging.info(f"Processing {len(payload_list)} payload(s) for upload")

            # Process each payload individually
            success_count = 0
            total_count = len(payload_list)

            for i, payload in enumerate(payload_list):
                logging.info(f"Processing payload {i + 1}/{total_count}")

                if self._upload_single_agent_run(payload):
                    success_count += 1
                    logging.info(f"✅ Payload {i + 1}/{total_count} uploaded successfully")
                else:
                    logging.error(f"❌ Payload {i + 1}/{total_count} failed to upload")

            # Return True only if ALL uploads succeed
            all_succeeded = success_count == total_count
            if all_succeeded:
                logging.info(f"✅ All {total_count} payload(s) uploaded successfully")
            else:
                logging.error(f"❌ {total_count - success_count}/{total_count} payload(s) failed to upload")

            return all_succeeded

        except Exception as e:
            logging.error(f"Error in batch upload processing: {e}")
            return False
