"""
Schema definitions for the API
"""

from .inputs import UserContext, ModelRequest, BatchModelRequestItem, BatchModelRequest
from .outputs import ModelResponse, BatchModelResponse

__all__ = [
    # Model Inputs
    "UserContext",
    "ModelRequest",
    "BatchModelRequestItem",
    "BatchModelRequest",
    # Model Outputs
    "ModelResponse",
    "BatchModelResponse",
]
