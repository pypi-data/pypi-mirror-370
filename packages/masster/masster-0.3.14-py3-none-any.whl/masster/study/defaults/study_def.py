"""Parameter class for Study core parameters."""

from dataclasses import dataclass, field
from typing import Optional, Any


@dataclass
class study_defaults:
    """
    Parameter class for Study core parameters.

    This class encapsulates parameters for study initialization, logging configuration,
    and folder management for multi-sample mass spectrometry studies.

    Attributes:
        folder (Optional[str]): Default directory for study files and outputs. Default is None.
        label (Optional[str]): Optional label to identify the study. Default is None.
        log_level (str): Logging level to be set for the logger. Default is "INFO".
        log_label (Optional[str]): Optional label for the logger. Default is None.
        log_sink (str): Output sink for logging. Default is "sys.stdout".
    """

    folder: Optional[str] = None
    label: str | None = None
    log_level: str = "INFO"
    log_label: Optional[str] = None
    log_sink: str = "sys.stdout"
    polarity: str = "positive"

    _param_metadata: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "folder": {
                "dtype": "Optional[str]",
                "description": "Default directory for study files and outputs",
                "default": None,
            },
            "label": {
                "dtype": "Optional[str]",
                "description": "Optional label to identify the study",
                "default": None,
            },
            "log_level": {
                "dtype": str,
                "description": "Logging level to be set for the logger",
                "default": "INFO",
                "allowed_values": ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            },
            "log_label": {
                "dtype": "Optional[str]",
                "description": "Optional label for the logger",
                "default": None,
            },
            "log_sink": {
                "dtype": str,
                "description": "Output sink for logging. Use 'sys.stdout' for console output, or a file path",
                "default": "sys.stdout",
            },
            "polarity": {
                "dtype": str,
                "description": "Polarity of the study (positive/negative)",
                "default": "positive",
                "allowed_values": ["positive", "negative", "pos", "neg"],
            },
        },
        repr=False,
    )

    def get_info(self, param_name: str) -> dict[str, Any]:
        """
        Get information about a specific parameter.

        Args:
            param_name: Name of the parameter

        Returns:
            Dictionary containing parameter metadata

        Raises:
            KeyError: If parameter name is not found
        """
        if param_name not in self._param_metadata:
            raise KeyError(f"Parameter '{param_name}' not found")
        return self._param_metadata[param_name]

    def get_description(self, param_name: str) -> str:
        """
        Get description for a specific parameter.

        Args:
            param_name: Name of the parameter

        Returns:
            Parameter description string
        """
        return str(self.get_info(param_name)["description"])

    def validate(self, param_name: str, value: Any) -> bool:
        """
        Validate a parameter value against its constraints.

        Args:
            param_name: Name of the parameter
            value: Value to validate

        Returns:
            True if value is valid, False otherwise
        """
        if param_name not in self._param_metadata:
            return False

        metadata = self._param_metadata[param_name]
        expected_dtype = metadata["dtype"]

        # Handle optional types
        if isinstance(expected_dtype, str) and expected_dtype.startswith("Optional"):
            if value is None:
                return True
            # Extract the inner type for validation
            if "str" in expected_dtype:
                expected_dtype = str
            elif "float" in expected_dtype:
                expected_dtype = float
            elif "int" in expected_dtype:
                expected_dtype = int

        # Type checking
        if expected_dtype is int:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    return False
        elif expected_dtype is float:
            if not isinstance(value, (int, float)):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    return False
        elif expected_dtype is bool:
            if not isinstance(value, bool):
                return False
        elif expected_dtype is str:
            if not isinstance(value, str):
                return False

        # Range validation for numeric types
        if expected_dtype in (int, float) and isinstance(value, (int, float)):
            if "min_value" in metadata and value < metadata["min_value"]:
                return False
            if "max_value" in metadata and value > metadata["max_value"]:
                return False

        # Allowed values validation for strings
        if expected_dtype is str and "allowed_values" in metadata:
            if value not in metadata["allowed_values"]:
                return False

        return True

    def set(self, param_name: str, value: Any, validate: bool = True) -> bool:
        """
        Set a parameter value with optional validation.

        Args:
            param_name: Name of the parameter
            value: New value for the parameter
            validate: Whether to validate the value before setting

        Returns:
            True if parameter was set successfully, False otherwise
        """
        if not hasattr(self, param_name):
            return False

        if validate and not self.validate(param_name, value):
            return False

        # Convert to expected type if needed
        if param_name in self._param_metadata:
            expected_dtype = self._param_metadata[param_name]["dtype"]

            # Handle optional types
            if isinstance(expected_dtype, str) and expected_dtype.startswith("Optional") and value is not None:
                if "int" in expected_dtype and not isinstance(value, int):
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        if validate:
                            return False
                elif "float" in expected_dtype and not isinstance(value, float):
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        if validate:
                            return False

        setattr(self, param_name, value)
        return True

    def get(self, param_name: str) -> Any:
        """
        Get the value of a parameter by name.

        Args:
            param_name: Name of the parameter

        Returns:
            Current value of the parameter
        """
        if not hasattr(self, param_name):
            raise KeyError(f"Parameter '{param_name}' not found")
        return getattr(self, param_name)

    def set_from_dict(
        self,
        param_dict: dict[str, Any],
        validate: bool = True,
    ) -> list[str]:
        """
        Update multiple parameters from a dictionary.

        Args:
            param_dict: Dictionary of parameter names and values
            validate: Whether to validate values before setting

        Returns:
            List of parameter names that could not be set
        """
        failed_params = []

        for param_name, value in param_dict.items():
            if not self.set(param_name, value, validate):
                failed_params.append(param_name)

        return failed_params

    def to_dict(self) -> dict[str, Any]:
        """
        Convert parameters to dictionary, excluding metadata.

        Returns:
            Dictionary of parameter names and values
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def list_parameters(self) -> list[str]:
        """
        Get list of all parameter names.

        Returns:
            List of parameter names
        """
        return [k for k in self.__dict__.keys() if not k.startswith("_")]

    def validate_all(self) -> tuple[bool, list[str]]:
        """
        Validate all parameters in the instance.

        Returns:
            Tuple of (all_valid, list_of_invalid_params)
            - all_valid: True if all parameters are valid, False otherwise
            - list_of_invalid_params: List of parameter names that failed validation
        """
        invalid_params = []

        for param_name in self.list_parameters():
            if param_name in self._param_metadata:
                current_value = getattr(self, param_name)
                if not self.validate(param_name, current_value):
                    invalid_params.append(param_name)

        return len(invalid_params) == 0, invalid_params
