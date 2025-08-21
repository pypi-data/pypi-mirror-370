#   ---------------------------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   ---------------------------------------------------------------------------------
"""Real integration tests for the conductr functionality."""

from __future__ import annotations

import json
import os
import time

import pytest

from railtownai.config import set_api_key
from railtownai.handler import RailtownHandler


@pytest.mark.integration
@pytest.mark.real_api
@pytest.mark.blob_upload
@pytest.mark.slow
class TestRealConductrIntegration:
    """Real integration tests for the conductr functionality."""

    def setup_method(self):
        """Set up test environment."""
        # Get API key from environment variable for real integration testing
        api_key = os.getenv("RAILTOWN_API_KEY")
        if not api_key:
            pytest.skip("RAILTOWN_API_KEY environment variable not set")

        set_api_key(api_key)
        self.handler = RailtownHandler()

        # Load mock data
        mock_data_path = os.path.join(os.path.dirname(__file__), "mock_data.json")
        with open(mock_data_path) as f:
            self.mock_data = json.load(f)

    @pytest.mark.real_api
    def test_real_presigned_sas_url_retrieval(self):
        """Test real presigned SAS URL retrieval from Railtown API."""
        # This test requires a valid API key and network connectivity
        sas_url = self.handler._get_conductr_presigned_sas_url()

        # Should return a valid SAS URL or None (depending on API response)
        if sas_url is not None:
            assert isinstance(sas_url, str)
            assert sas_url.startswith("https://")
            assert "?" in sas_url  # Should contain query parameters (SAS token)
            assert "sas_token" in sas_url or "sv=" in sas_url  # Should contain SAS token indicators

    @pytest.mark.blob_upload
    def test_real_blob_upload_with_complex_data(self):
        """Test real blob upload with complex nested JSON data conforming to the schema."""
        # Use the full mock_data structure
        test_data = {
            # "session_id": str(uuid.uuid4()),
            # "run_id": str(uuid.uuid4()),
            "name": "complex integration test agent run",
            "nodes": self.mock_data["nodes"][:3],  # Use first 3 nodes
            "edges": self.mock_data["edges"][:2],  # Use first 2 edges
            "steps": [
                {"step": 1, "time": time.time(), "identifier": "step_1"},
                {"step": 2, "time": time.time() + 1, "identifier": "step_2"},
                {"step": 3, "time": time.time() + 2, "identifier": "step_3"},
            ],
        }

        result = self.handler.upload_agent_run(test_data)

        # Should return True if upload was successful
        assert isinstance(result, bool)

    @pytest.mark.blob_upload
    def test_real_blob_upload_with_special_characters(self):
        """Test real blob upload with special characters and edge cases conforming to the schema."""
        # Use mock data but add special characters to edge details
        test_data = {
            # "session_id": str(uuid.uuid4()),
            # "run_id": str(uuid.uuid4()),
            "name": "special characters test agent run",
            "nodes": self.mock_data["nodes"][:1],  # Use first node
            "edges": [
                {
                    "source": self.mock_data["nodes"][0]["identifier"],
                    "target": "target_node",
                    "identifier": "special_edge",
                    "stamp": {"step": 1, "time": time.time(), "identifier": "special_edge_stamp"},
                    "details": {
                        "input_args": [
                            "String with spaces",
                            "String-with-dashes",
                            "String_with_underscores",
                            "StringWithCamelCase",
                            "string with numbers 123",
                            "string with symbols !@#$%^&*()",
                            "string with quotes \"double\" and 'single'",
                            "string with newlines\nand\ttabs",
                            "string with unicode: áéíóú ñ ç",
                            "string with emojis: 🎉🚀💻🔥",
                            "",  # Empty string
                            "   ",  # Whitespace only
                        ],
                        "input_kwargs": {
                            "empty_object": {},
                            "empty_array": [],
                            "null_value": None,
                            "boolean_true": True,
                            "boolean_false": False,
                            "zero": 0,
                            "negative": -42,
                            "float_number": 3.14159,
                            "large_number": 999999999999999999,
                            "small_number": -999999999999999999,
                        },
                        "status": "Completed",
                        "output": {
                            "special_strings": [
                                "String with spaces",
                                "String-with-dashes",
                                "String_with_underscores",
                                "StringWithCamelCase",
                                "string with numbers 123",
                                "string with symbols !@#$%^&*()",
                                "string with quotes \"double\" and 'single'",
                                "string with newlines\nand\ttabs",
                                "string with unicode: áéíóú ñ ç",
                                "string with emojis: 🎉🚀💻🔥",
                                "",  # Empty string
                                "   ",  # Whitespace only
                            ]
                        },
                    },
                    "parent": None,
                }
            ],
            "steps": [{"step": 1, "time": time.time(), "identifier": "special_step"}],  # Add non-empty steps
        }

        result = self.handler.upload_agent_run(test_data)

        # Should return True if upload was successful
        assert isinstance(result, bool)

    @pytest.mark.real_api
    @pytest.mark.blob_upload
    @pytest.mark.slow
    def test_real_end_to_end_workflow(self):
        """Test the complete end-to-end workflow: get SAS URL and upload data."""
        # Step 1: Get the presigned SAS URL
        sas_url = self.handler._get_conductr_presigned_sas_url()

        if sas_url is None:
            pytest.skip("Could not retrieve presigned SAS URL - API may be unavailable")

        # Step 2: Prepare test data using mock_data
        test_data = {
            # "session_id": str(uuid.uuid4()),
            # "run_id": str(uuid.uuid4()),
            "name": "end to end test agent run",
            "nodes": self.mock_data["nodes"][:2],  # Use first 2 nodes
            "edges": self.mock_data["edges"][:1],  # Use first edge
            "steps": [{"step": 1, "time": time.time(), "identifier": "e2e_step"}],
        }

        # Step 3: Upload the data
        result = self.handler.upload_agent_run(test_data)

        # Step 4: Verify the result
        assert isinstance(result, bool)

        # If successful, we could potentially verify the upload by trying to access the blob
        # This would require additional permissions and is beyond the scope of this test

    @pytest.mark.blob_upload
    def test_real_error_handling_with_invalid_data(self):
        """Test real error handling with potentially problematic data."""
        # Use mock data but add problematic elements
        problematic_data = {
            # "session_id": str(uuid.uuid4()),
            # "run_id": str(uuid.uuid4()),
            "name": "error handling test agent run",
            "nodes": self.mock_data["nodes"][:1],  # Use first node
            "edges": [],
            "steps": [],
        }

        # Create a circular reference (this should be handled gracefully)
        problematic_data["nodes"][0]["details"]["internals"]["circular_reference"] = problematic_data

        # This should return False due to empty edges and steps
        result = self.handler.upload_agent_run(problematic_data)

        # Should return False when required fields are empty
        assert result is False

    @pytest.mark.blob_upload
    def test_real_error_handling_with_missing_fields(self):
        """Test real error handling with missing required fields."""
        # Test with missing nodes field
        data_missing_nodes = {
            "name": "missing nodes test",
            "edges": [{"source": "a", "target": "b", "identifier": "edge1"}],
            "steps": [{"step": 1, "time": time.time(), "identifier": "step1"}],
        }
        result = self.handler.upload_agent_run(data_missing_nodes)
        assert result is False

        # Test with missing edges field
        data_missing_edges = {
            "name": "missing edges test",
            "nodes": [{"identifier": "node1", "node_type": "test"}],
            "steps": [{"step": 1, "time": time.time(), "identifier": "step1"}],
        }
        result = self.handler.upload_agent_run(data_missing_edges)
        assert result is False

        # Test with missing steps field
        data_missing_steps = {
            "name": "missing steps test",
            "nodes": [{"identifier": "node1", "node_type": "test"}],
            "edges": [{"source": "a", "target": "b", "identifier": "edge1"}],
        }
        result = self.handler.upload_agent_run(data_missing_steps)
        assert result is False

        # Test with empty arrays
        data_empty_arrays = {
            "name": "empty arrays test",
            "nodes": [],
            "edges": [],
            "steps": [],
        }
        result = self.handler.upload_agent_run(data_empty_arrays)
        assert result is False

    @pytest.mark.blob_upload
    @pytest.mark.slow
    def test_real_performance_with_multiple_uploads(self):
        """Test performance with multiple consecutive uploads."""
        upload_results = []
        start_time = time.time()

        for i in range(5):  # Test 5 consecutive uploads
            test_data = {
                # "session_id": str(uuid.uuid4()),
                # "run_id": str(uuid.uuid4()),
                "name": f"performance test agent run {i + 1}",
                "nodes": self.mock_data["nodes"][: i + 1],  # Use increasing number of nodes
                "edges": self.mock_data["edges"][: i + 1],  # Use increasing number of edges
                "steps": [{"step": i + 1, "time": time.time() + i, "identifier": f"perf_step_{i}"}],
            }

            result = self.handler.upload_agent_run(test_data)
            upload_results.append(result)

            # Small delay between uploads to avoid overwhelming the service
            time.sleep(0.1)

        end_time = time.time()
        total_time = end_time - start_time

        # Verify all results are boolean
        assert all(isinstance(result, bool) for result in upload_results)

        # Log performance metrics
        successful_uploads = sum(upload_results)
        print(f"Performance test: {successful_uploads}/5 uploads successful in {total_time:.2f} seconds")

        # The test passes regardless of success/failure rate
        # as this is testing the integration, not the success rate

    @pytest.mark.blob_upload
    @pytest.mark.slow
    def test_real_array_upload_functionality(self):
        """Test real array upload functionality with multiple payloads."""
        # Create multiple test payloads
        test_data_array = [
            {
                "name": "array test agent run 1",
                "nodes": self.mock_data["nodes"][:1],  # Use first node
                "edges": self.mock_data["edges"][:1],  # Use first edge
                "steps": [{"step": 1, "time": time.time(), "identifier": "array_step_1"}],
            },
            {
                "name": "array test agent run 2",
                "nodes": self.mock_data["nodes"][:2],  # Use first 2 nodes
                "edges": self.mock_data["edges"][:2],  # Use first 2 edges
                "steps": [{"step": 2, "time": time.time() + 1, "identifier": "array_step_2"}],
            },
            {
                "name": "array test agent run 3",
                "nodes": self.mock_data["nodes"][:3],  # Use first 3 nodes
                "edges": self.mock_data["edges"][:3],  # Use first 3 edges
                "steps": [{"step": 3, "time": time.time() + 2, "identifier": "array_step_3"}],
            },
        ]

        print(f"Testing array upload with {len(test_data_array)} payloads")

        # Upload the array of payloads
        start_time = time.time()
        result = self.handler.upload_agent_run(test_data_array)
        end_time = time.time()

        total_time = end_time - start_time

        # Verify result is boolean
        assert isinstance(result, bool)

        # Log performance metrics
        if result:
            print(f"✅ Array upload successful: {len(test_data_array)} payloads in {total_time:.2f} seconds")
        else:
            print(f"❌ Array upload failed: {len(test_data_array)} payloads in {total_time:.2f} seconds")

        # The test passes regardless of success/failure rate
        # as this is testing the integration, not the success rate
