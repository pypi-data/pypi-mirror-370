"""
Module provides a class to fetch weather data from the BrightSky API.

Args:
    latitude: The latitude of the location.
    longitude: The longitude of the location.

"""

import requests

from brownllama.logger import get_logger

logger = get_logger(__name__)


class Weather:
    """A class to fetch weather data from the BrightSky API."""

    def __init__(self, latitude: float, longitude: float) -> None:
        """
        Initialize the WeatherFetcher with latitude and longitude.

        Args:
            latitude: The latitude of the location.
            longitude: The longitude of the location.

        """
        self.latitude = latitude
        self.longitude = longitude
        self.api_url = "https://api.brightsky.dev/current_weather"

    def get_weather(self) -> str:
        """
        Fetch weather data from the BrightSky API.

        Returns:
            A dictionary containing the weather data.

        """
        try:
            headers = {"Accept": "application/json"}
            params = {
                "lat": self.latitude,
                "lon": self.longitude,
            }

            logger.debug(f"Making API request to: {self.api_url} with params: {params}")
            response = requests.get(
                self.api_url, headers=headers, params=params, timeout=60
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as err_http:
            logger.debug(f"HTTP error occurred: {err_http}")
        except requests.exceptions.ConnectionError as err_conn:
            logger.debug(f"Connection error occurred: {err_conn}")
        except requests.exceptions.Timeout as err_timeout:
            logger.debug(f"Timeout error occurred: {err_timeout}")
        except requests.exceptions.RequestException as err:
            logger.debug(f"An error occurred during the API request: {err}")
        except (IndexError, KeyError) as err:
            logger.debug(f"Could not parse the JSON response: {err}")

        return "unknown"
