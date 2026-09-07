"""Custom exceptions for the Food Defect AOI pipeline."""


class AOIException(Exception):
    """Base exception for all AOI operations."""


class ModelLoadError(AOIException):
    """Raised when the ONNX or PyTorch model fails to load."""


class InferenceError(AOIException):
    """Raised when inference execution fails."""


class ImageDecodeError(AOIException):
    """Raised when the input image cannot be decoded."""


class NoObjectDetectedError(AOIException):
    """Raised when no fruit object is identified in the inspection frame."""
