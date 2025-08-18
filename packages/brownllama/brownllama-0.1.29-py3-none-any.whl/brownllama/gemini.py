"""
Google AI Studio.

This module provides a class for generating responses, chat using the GenAI API.
"""

from google import genai


class GenAI:
    """A class for generating responses using the GenAI API."""

    def __init__(self, api_key: str) -> None:
        """
        Initialize the GenAIResponseGenerator class.

        Args:
            api_key (str): The API key for accessing the GenAI API.

        """
        genai.configure(api_key=api_key)
        self.client = genai.Client()
        self.model = "gemini-2.5-flash"

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using the GenAI API.

        Args:
            prompt (str): The prompt for generating the response.

        Returns:
            The generated response.

        """
        return self.client.models.generate_content(model=self.model, contents=prompt)
