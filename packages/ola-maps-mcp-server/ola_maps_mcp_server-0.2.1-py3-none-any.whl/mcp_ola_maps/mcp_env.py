"""Environment configuration for the MCP Ola Maps server.

This module handles all environment variable configuration with sensible defaults
and type conversion.
"""

from dataclasses import dataclass
import os
from typing import Optional

@dataclass
class OlaMapsConfig:
    """Configuration for Ola Maps connection settings.

    This class handles all environment variable configuration with sensible defaults
    and type conversion. It provides typed methods for accessing each configuration value.

    Required environment variables:
        OLA_MAPS_API_KEY: API key in String format to authenticate and access ola maps APIs
    """

    def __init__(self):
        """Initialize the configuration from environment variables."""
        self._validate_required_vars()

    @property
    def api_key(self) -> str:
        """Get the Ola Maps API Key."""
        return os.environ["OLA_MAPS_API_KEY"]

    def get_api_key(self) -> dict:
        """Get the configuration dictionary for Ola maps authentication.

        Returns:
            string: API key passed tools for API authentication.
        """
        return self.api_key

    def _validate_required_vars(self) -> None:
        """Validate that all required environment variables are set.

        Raises:
            ValueError: If any required environment variable is missing.
        """
        missing_vars = []
        for var in ["OLA_MAPS_API_KEY"]:
            if var not in os.environ:
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )


# Global instance for easy access
config = OlaMapsConfig()