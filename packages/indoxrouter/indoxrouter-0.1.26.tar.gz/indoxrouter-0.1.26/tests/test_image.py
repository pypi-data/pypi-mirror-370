"""
Test the image generation functionality of the IndoxRouter client.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
from indoxrouter import Client


class TestImageGeneration(unittest.TestCase):
    """Test the image generation functionality."""

    def setUp(self):
        """Set up the test case."""
        # Use a mock API key for testing
        self.api_key = "test_api_key"

        # Create a patched client that doesn't make real API calls
        with patch("indoxrouter.client.requests.Session") as mock_session:
            # Mock successful authentication response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"access_token": "mock_token"}
            mock_session.return_value.post.return_value = mock_response

            # Create client with mocked session
            self.client = Client(api_key=self.api_key)
            self.client._request = MagicMock()  # Replace _request with mock

    def test_image_generation_response_format(self):
        """Test that the image generation response format is correct."""
        # Mock response data that matches what we expect from the server
        mock_response = {
            "request_id": "test-request-id",
            "created_at": "2025-05-29T11:39:24.621706",
            "duration_ms": 12340.412378311157,
            "provider": "openai",
            "model": "dall-e-2",
            "success": True,
            "message": "",
            "usage": {
                "tokens_prompt": 0,
                "tokens_completion": 0,
                "tokens_total": 0,
                "cost": 0.016,
                "latency": 12.240789651870728,
                "timestamp": "2025-05-29T11:39:24.612377",
            },
            "data": [
                {
                    "url": "https://example.com/generated-image.png",
                    "revised_prompt": "A beautiful sunset over the ocean with clouds.",
                }
            ],
        }

        # Set the mock response for the _request method
        self.client._request.return_value = mock_response

        # Call the images method
        response = self.client.images(
            prompt="A beautiful sunset over the ocean",
            model="openai/dall-e-2",
            size="1024x1024",
        )

        # Verify the client made the request with the correct parameters
        self.client._request.assert_called_once()
        call_args = self.client._request.call_args[0]

        # Verify the response format
        self.assertEqual(response["success"], True)
        self.assertEqual(response["provider"], "openai")
        self.assertEqual(response["model"], "dall-e-2")

        # Verify the data contains the image URL
        self.assertIn("data", response)
        self.assertIsInstance(response["data"], list)
        self.assertEqual(len(response["data"]), 1)
        self.assertIn("url", response["data"][0])
        self.assertEqual(
            response["data"][0]["url"], "https://example.com/generated-image.png"
        )

        # Verify usage information
        self.assertIn("usage", response)
        self.assertIn("cost", response["usage"])
        self.assertGreater(response["usage"]["cost"], 0)


if __name__ == "__main__":
    unittest.main()
