"""
CaseConverter.

A class to convert keys in a list of dictionaries to snake_case, camelCase, or kebab-case.

"""


class CaseConverter:
    """
    CaseConverter.

    A class to convert keys in a list of dictionaries to snake_case, camelCase, or kebab-case.

    """

    def __init__(self, raw_data: list[dict]) -> None:
        """
        Initialize the converter with the input data.

        Accepts a list of Python dictionaries.

        Args:
            raw_data: A list of Python dictionaries.

        """
        self.original_data = raw_data

    @staticmethod
    def _convert_key(key: str, case_type: str) -> str:
        """
        Convert a single key string to the specified case type.

        Args:
            key: The original key string (e.g., "Package Name", "Date").
            case_type: The target case type ('snake', 'camel', 'kebab').

        Returns:
            The converted key string.

        Raises:
            ValueError: If the case_type is not supported.

        """
        normalized_key = key.replace(" ", "_").lower()

        if case_type == "snake":
            return normalized_key

        if case_type == "camel":
            parts = normalized_key.split("_")
            # First part is lowercase, subsequent parts are title-cased
            return parts[0] + "".join(word.title() for word in parts[1:])

        if case_type == "kebab":
            return normalized_key.replace("_", "-")

        error_message = (
            f"Unsupported case_type: {case_type}. Choose 'snake', 'camel', or 'kebab'."
        )
        raise ValueError(error_message)

    def _get_converted_data(self, case_type: str) -> list[dict]:
        """
        Convert Data.

        Converts keys in dictionaries to the specified case type and returns
        them as a list of dictionaries. This is a helper method for internal use.

        Args:
            case_type: The target case type ('snake', 'camel', 'kebab').

        Returns:
            A list of dictionaries with keys converted to the specified case type.

        """
        processed_data = []
        for data in self.original_data:
            new_data = {}
            for key, value in data.items():
                new_key = self._convert_key(key, case_type)
                new_data[new_key] = value
            processed_data.append(new_data)
        return processed_data

    def snake_case(self) -> list[dict]:
        """
        Convert all dictionary keys in the data to snake_case.

        Returns:
            A list of dictionaries with keys converted to snake_case.

        """
        return self._get_converted_data("snake")

    def camel_case(self) -> list[dict]:
        """
        Convert all dictionary keys in the data to camelCase.

        Returns:
            A list of dictionaries with keys converted to camelCase.

        """
        return self._get_converted_data("camel")

    def kebab_case(self) -> list[dict]:
        """
        Convert all dictionary keys in the data to kebab-case.

        Returns:
            A list of dictionaries with keys converted to kebab-case.

        """
        return self._get_converted_data("kebab")
