#!/usr/bin/env python3
"""
Pydantic Schemas for Voice-to-ISL Translation API
Real-time Bidirectional Voice-to-ISL & ISL-to-Voice Translation System

This module defines all the request/response schemas for the FastAPI application,
ensuring proper data validation and API documentation.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class VoiceInput(BaseModel):
    """
    Schema for voice input requests to the translation API.
    
    This represents the simulated transcription of user's voice input
    for the MVS implementation.
    """
    audio_text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The simulated transcription of the user's voice input",
        example="Hello, how are you?"
    )
    
    @validator('audio_text')
    def validate_audio_text(cls, v):
        """Validate that audio_text is not empty after stripping whitespace."""
        if not v or not v.strip():
            raise ValueError("audio_text cannot be empty or contain only whitespace")
        return v.strip()

    class Config:
        """Pydantic configuration for VoiceInput schema."""
        schema_extra = {
            "example": {
                "audio_text": "Hello, how are you today?"
            }
        }


class ISLOutput(BaseModel):
    """
    Schema for ISL translation output responses.
    
    Contains the complete translation result including source text,
    ISL gloss notation, avatar stream URL, and metadata.
    """
    source_text: str = Field(
        ...,
        description="The original transcribed text input",
        example="Hello, how are you?"
    )
    
    isl_gloss: str = Field(
        ...,
        description="The ISL gloss notation representing the signed translation",
        example="HELLO HOW YOU?"
    )
    
    avatar_stream_url: str = Field(
        ...,
        description="WebSocket URL or identifier for the 3D avatar animation stream",
        example="ws://localhost:8000/avatar/stream/avatar_pose_stream_a1b2c3d4_1635123456"
    )
    
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for the translation quality (0.0 to 1.0)",
        example=0.92
    )
    
    processing_time_ms: float = Field(
        ...,
        ge=0.0,
        description="Total processing time in milliseconds",
        example=234.56
    )

    class Config:
        """Pydantic configuration for ISLOutput schema."""
        schema_extra = {
            "example": {
                "source_text": "Hello, how are you?",
                "isl_gloss": "HELLO HOW YOU?",
                "avatar_stream_url": "ws://localhost:8000/avatar/stream/avatar_pose_stream_a1b2c3d4_1635123456",
                "confidence": 0.92,
                "processing_time_ms": 234.56
            }
        }


class StatusResponse(BaseModel):
    """
    Schema for general status responses from the API.
    
    Used for basic endpoint responses and operation confirmations.
    """
    status: str = Field(
        ...,
        description="Status of the operation",
        example="success"
    )
    
    message: str = Field(
        ...,
        description="Descriptive message about the operation",
        example="Voice-to-ISL Translation API is running"
    )
    
    timestamp: datetime = Field(
        ...,
        description="Timestamp when the response was generated",
        example="2024-10-25T10:30:00.000Z"
    )

    class Config:
        """Pydantic configuration for StatusResponse schema."""
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Voice-to-ISL Translation API is running",
                "timestamp": "2024-10-25T10:30:00.000Z"
            }
        }


class HealthCheck(BaseModel):
    """
    Schema for health check responses.
    
    Provides detailed information about system health and operational metrics.
    """
    status: str = Field(
        ...,
        description="Overall health status of the system",
        example="healthy"
    )
    
    uptime_seconds: int = Field(
        ...,
        ge=0,
        description="System uptime in seconds since startup",
        example=3600
    )
    
    service_status: str = Field(
        ...,
        description="Current operational status of core services",
        example="operational"
    )
    
    translations_processed: int = Field(
        ...,
        ge=0,
        description="Total number of translations processed since startup",
        example=142
    )
    
    timestamp: datetime = Field(
        ...,
        description="Timestamp when the health check was performed",
        example="2024-10-25T10:30:00.000Z"
    )

    class Config:
        """Pydantic configuration for HealthCheck schema."""
        schema_extra = {
            "example": {
                "status": "healthy",
                "uptime_seconds": 3600,
                "service_status": "operational",
                "translations_processed": 142,
                "timestamp": "2024-10-25T10:30:00.000Z"
            }
        }


class ErrorResponse(BaseModel):
    """
    Schema for error responses from the API.
    
    Provides structured error information for client applications.
    """
    error: 'ErrorDetail' = Field(
        ...,
        description="Detailed error information"
    )

    class Config:
        """Pydantic configuration for ErrorResponse schema."""
        schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Input validation failed: audio_text cannot be empty",
                    "details": {"field": "audio_text", "issue": "empty_value"},
                    "timestamp": "2024-10-25T10:30:00.000Z",
                    "trace_id": "abc123def456"
                }
            }
        }


class ErrorDetail(BaseModel):
    """
    Schema for detailed error information.
    
    Contains specific error codes, messages, and debugging information.
    """
    code: str = Field(
        ...,
        description="Machine-readable error code",
        example="VALIDATION_ERROR"
    )
    
    message: str = Field(
        ...,
        description="Human-readable error message",
        example="Input validation failed: audio_text cannot be empty"
    )
    
    details: Optional[dict] = Field(
        None,
        description="Additional error details and context",
        example={"field": "audio_text", "issue": "empty_value"}
    )
    
    timestamp: datetime = Field(
        ...,
        description="Timestamp when the error occurred",
        example="2024-10-25T10:30:00.000Z"
    )
    
    trace_id: Optional[str] = Field(
        None,
        description="Unique identifier for error tracking and debugging",
        example="abc123def456"
    )

    class Config:
        """Pydantic configuration for ErrorDetail schema."""
        schema_extra = {
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed: audio_text cannot be empty",
                "details": {"field": "audio_text", "issue": "empty_value"},
                "timestamp": "2024-10-25T10:30:00.000Z",
                "trace_id": "abc123def456"
            }
        }


# Additional schemas for future expansion (ISL-to-Voice functionality)

class ISLInput(BaseModel):
    """
    Schema for ISL input requests (for future ISL-to-Voice translation).
    
    This would be used for the reverse translation workflow.
    """
    video_data: str = Field(
        ...,
        description="Base64 encoded video data containing ISL gestures",
        example="UklGRnoGAABXQVZFZm10IBAAAAABAAEA..."
    )
    
    pose_data: Optional[dict] = Field(
        None,
        description="Pre-extracted pose data if available",
        example={"landmarks": [], "confidence": 0.95}
    )
    
    format: str = Field(
        "webm",
        description="Video format",
        example="webm"
    )
    
    frame_rate: int = Field(
        30,
        ge=15,
        le=60,
        description="Video frame rate",
        example=30
    )

    class Config:
        """Pydantic configuration for ISLInput schema."""
        schema_extra = {
            "example": {
                "video_data": "UklGRnoGAABXQVZFZm10IBAAAAABAAEA...",
                "pose_data": {"landmarks": [], "confidence": 0.95},
                "format": "webm",
                "frame_rate": 30
            }
        }


class VoiceOutput(BaseModel):
    """
    Schema for voice output responses (for future ISL-to-Voice translation).
    
    Contains the translation result from ISL to spoken language.
    """
    source_gloss: str = Field(
        ...,
        description="The original ISL gloss notation",
        example="HELLO HOW YOU?"
    )
    
    transcribed_text: str = Field(
        ...,
        description="The natural language text translation",
        example="Hello, how are you?"
    )
    
    audio_stream_url: str = Field(
        ...,
        description="URL for the synthesized speech audio stream",
        example="ws://localhost:8000/audio/stream/voice_stream_123"
    )
    
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Translation confidence score",
        example=0.88
    )
    
    processing_time_ms: float = Field(
        ...,
        ge=0.0,
        description="Processing time in milliseconds",
        example=456.78
    )

    class Config:
        """Pydantic configuration for VoiceOutput schema."""
        schema_extra = {
            "example": {
                "source_gloss": "HELLO HOW YOU?",
                "transcribed_text": "Hello, how are you?",
                "audio_stream_url": "ws://localhost:8000/audio/stream/voice_stream_123",
                "confidence": 0.88,
                "processing_time_ms": 456.78
            }
        }


# Update forward references for proper schema resolution
ErrorResponse.model_rebuild()
