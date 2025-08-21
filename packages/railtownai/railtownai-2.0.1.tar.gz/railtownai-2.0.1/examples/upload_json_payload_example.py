#!/usr/bin/env python3
"""
Simple example demonstrating the upload_agent_run method

This example shows how to directly use the public method to upload a minimal JSON payload
to Railtown AI's blob storage using presigned SAS URLs.
"""

import json
import os
import uuid
from typing import Any

import railtownai


def create_simple_test_data(run_id: str | None = None, session_id: str | None = None) -> dict[str, Any]:
    """
    Load mock data from the JSON file for upload testing.

    Returns:
        Dict containing mock test data from tests/integration/mock_data.json
    """
    # Get the path to the mock data file relative to the project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    mock_data_path = os.path.join(project_root, "tests", "integration", "mock_data.json")

    try:
        with open(mock_data_path) as f:
            data = json.load(f)

            if session_id:
                data["session_id"] = session_id

            else:
                data["session_id"] = str(uuid.uuid4())

            if run_id:
                data["run_id"] = run_id
            else:
                data["run_id"] = str(uuid.uuid4())

            return data
    except FileNotFoundError:
        print(f"Warning: Mock data file not found at {mock_data_path}")
        print("Falling back to simple test data...")
        return {"name": "flight planner", "nodes": [], "edges": [], "stamps": []}
    except json.JSONDecodeError as e:
        print(f"Warning: Error parsing mock data file: {e}")
        print("Falling back to simple test data...")
        return {"name": "flight planner", "nodes": [], "edges": [], "stamps": []}


def upload_json_payload_example():
    """
    Simple example demonstrating how to use upload_agent_run method.
    """
    print("Railtown AI Simple JSON Payload Upload Test")
    print("=" * 50)

    # Initialize Railtown AI with your API key
    # Replace 'YOUR_RAILTOWN_API_KEY' with your actual API key
    railtownai.init(os.getenv("RAILTOWN_API_KEY"))

    # Create simple test data
    test_data = create_simple_test_data()

    print("Test data to upload:")
    print(json.dumps(test_data, indent=2))

    # Upload the JSON payload (single payload)
    print("\nUploading single JSON payload...")
    success = railtownai.upload_agent_run(test_data)

    if success:
        print("✅ Single JSON payload uploaded successfully!")
    else:
        print("❌ Failed to upload single JSON payload")

    # Create multiple test data for array upload
    test_data_array = [create_simple_test_data(), create_simple_test_data(), create_simple_test_data()]

    print("\n" + "=" * 50)
    print("Uploading array of JSON payloads...")
    print(f"Array contains {len(test_data_array)} payloads")

    # Upload the array of JSON payloads
    success = railtownai.upload_agent_run(test_data_array)

    if success:
        print("✅ All JSON payloads in array uploaded successfully!")
    else:
        print("❌ Failed to upload one or more JSON payloads in array")

    print("\nTest completed!")


if __name__ == "__main__":
    # Note: Replace 'YOUR_RAILTOWN_API_KEY' with your actual API key
    # If you don't have one, the example will still run but uploads will fail

    upload_json_payload_example()
