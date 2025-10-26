#!/usr/bin/env python3
"""
FastAPI Backend for Voice-to-ISL Translation MVS
Real-time Bidirectional Voice-to-ISL & ISL-to-Voice Translation System

This module simulates the L4 Core Data Plane services (ASR, NLP Translator, Animation Engine)
and their coordination, exposed via the L2 API Gateway.
"""

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Dict, Any, Tuple
import logging
import time
import asyncio
from datetime import datetime

# Import schemas and avatar engine
from schemas import VoiceInput, ISLOutput, StatusResponse, HealthCheck
from avatar_engine import generate_avatar_animation
from websocket_handler import handle_avatar_websocket, avatar_stream_manager, cleanup_expired_streams_task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Voice-to-ISL Translation API",
    description="MVS implementation of the Voice-to-ISL translation system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Global application state
app_state: Dict[str, Any] = {
    "startup_time": datetime.now(),
    "translation_count": 0,
    "service_status": "operational"
}


def mock_asr_service(audio_text: str) -> str:
    """
    Mock ASR Service Simulation (Transcription)
    
    Args:
        audio_text: The simulated transcription of user's voice input
        
    Returns:
        str: The processed text tokens (same as input for MVS)
    """
    logger.info(f"ASR Service processing: {audio_text}")
    # Simulate processing time
    time.sleep(0.05)
    return audio_text.strip()


def text_to_isl_gloss(text_tokens: str) -> str:
    """
    Mock NLP Translator Simulation (Text-to-Gloss)
    
    Converts natural language text to ISL Gloss notation.
    This is a simplified mock implementation.
    
    Args:
        text_tokens: Natural language text
        
    Returns:
        str: ISL Gloss representation
    """
    logger.info(f"NLP Translator processing: {text_tokens}")
    
    # Simulate processing time
    time.sleep(0.1)
    
    # Mock text-to-gloss conversion rules
    gloss_mapping = {
        "hello": "HELLO",
        "hi": "HELLO",
        "how are you": "HOW YOU",
        "how are you?": "HOW YOU?",
        "good morning": "MORNING GOOD",
        "good evening": "EVENING GOOD",
        "thank you": "THANK-YOU",
        "please": "PLEASE",
        "sorry": "SORRY",
        "yes": "YES",
        "no": "NO",
        "my name is": "MY NAME",
        "nice to meet you": "NICE MEET YOU",
        "see you later": "SEE-YOU LATER",
        "goodbye": "GOODBYE",
        "help": "HELP",
        "water": "WATER",
        "food": "FOOD",
        "hospital": "HOSPITAL",
        "doctor": "DOCTOR",
        "school": "SCHOOL",
        "work": "WORK",
        "home": "HOME",
        "family": "FAMILY"
    }
    
    # Convert to lowercase for matching
    text_lower = text_tokens.lower().strip()
    
    # Try exact match first
    if text_lower in gloss_mapping:
        return gloss_mapping[text_lower]
    
    # Try partial matching for common phrases
    for phrase, gloss in gloss_mapping.items():
        if phrase in text_lower:
            # Replace the phrase and continue processing
            text_lower = text_lower.replace(phrase, gloss)
    
    # Basic word-by-word conversion for unmatched content
    words = text_lower.split()
    gloss_words = []
    
    for word in words:
        # Remove punctuation
        clean_word = word.strip(".,!?;:")
        if clean_word in gloss_mapping:
            gloss_words.append(gloss_mapping[clean_word])
        else:
            # Convert to uppercase as default gloss representation
            gloss_words.append(clean_word.upper())
    
    result_gloss = " ".join(gloss_words) if gloss_words else text_tokens.upper()
    
    # Ensure the result has ISL-like structure
    result_gloss = result_gloss.replace(" ARE ", " ").replace(" IS ", " ").replace(" THE ", " ")
    
    return result_gloss


def gloss_to_avatar_stream(isl_gloss: str) -> Tuple[str, Dict]:
    """
    Real Animation Engine (Gloss-to-Pose)
    
    Generates actual 3D avatar animation from ISL gloss using the Avatar Animation Engine.
    
    Args:
        isl_gloss: ISL Gloss sequence
        
    Returns:
        Tuple[str, Dict]: Avatar stream URL and animation data
    """
    logger.info(f"Animation Engine processing: {isl_gloss}")
    
    try:
        # Generate real avatar animation
        stream_url, animation_data = generate_avatar_animation(isl_gloss)
        
        logger.info(f"Generated avatar animation: {animation_data.get('frame_count')} frames, "
                   f"{animation_data.get('total_duration_seconds')}s duration")
        
        return stream_url, animation_data
        
    except Exception as e:
        logger.error(f"Avatar animation generation failed: {str(e)}")
        
        # Fallback to simple stream URL
        import hashlib
        gloss_hash = hashlib.md5(isl_gloss.encode()).hexdigest()[:8]
        stream_id = f"avatar_fallback_{gloss_hash}_{int(time.time())}"
        fallback_url = f"ws://localhost:8000/avatar/stream/{stream_id}"
        
        fallback_data = {
            "error": str(e),
            "fallback": True,
            "gloss_input": isl_gloss,
            "processing_time_ms": 0
        }
        
        return fallback_url, fallback_data


@app.get("/", response_model=StatusResponse)
async def root():
    """Root endpoint providing basic API information."""
    return StatusResponse(
        status="success",
        message="Voice-to-ISL Translation API is running",
        timestamp=datetime.now()
    )


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint for monitoring system status."""
    uptime_seconds = (datetime.now() - app_state["startup_time"]).total_seconds()
    
    return HealthCheck(
        status="healthy",
        uptime_seconds=int(uptime_seconds),
        service_status=app_state["service_status"],
        translations_processed=app_state["translation_count"],
        timestamp=datetime.now()
    )


@app.post("/api/v1/translate/voice-to-isl", response_model=ISLOutput)
async def translate_voice_to_isl(voice_input: VoiceInput):
    """
    Main translation endpoint: Voice to ISL
    
    Orchestrates the complete L4 Voice-to-ISL translation workflow:
    1. ASR Service Simulation (Transcription)
    2. NLP Translator Simulation (Text-to-Gloss)  
    3. Animation Engine Simulation (Gloss-to-Pose)
    
    Args:
        voice_input: VoiceInput schema containing audio_text
        
    Returns:
        ISLOutput: Complete translation result with gloss and avatar stream
        
    Raises:
        HTTPException: 400 if input validation fails
        HTTPException: 500 if translation processing fails
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting voice-to-ISL translation for: {voice_input.audio_text}")
        
        # Step 1: ASR Service Simulation (Transcription)
        transcribed_text = mock_asr_service(voice_input.audio_text)
        
        # Step 2: NLP Translator Simulation (Text-to-Gloss)
        isl_gloss = text_to_isl_gloss(transcribed_text)
        
        # Step 3: Animation Engine (Gloss-to-Pose) - Real Implementation
        avatar_stream_url, animation_data = gloss_to_avatar_stream(isl_gloss)
        
        # Store animation data for WebSocket streaming
        if isinstance(animation_data, dict) and not animation_data.get("fallback", False):
            # Extract stream ID from URL and cache animation data
            stream_id = avatar_stream_url.split('/')[-1]
            avatar_stream_manager.store_animation_data(stream_id, animation_data)
            logger.info(f"Cached animation data for WebSocket streaming: {stream_id}")
        
        # Calculate processing time
        processing_time = round((time.time() - start_time) * 1000, 2)  # Convert to milliseconds
        
        # Update application state
        app_state["translation_count"] += 1
        
        # Prepare response with animation data
        confidence_score = 0.92  # Base confidence
        
        # Adjust confidence based on animation generation success
        if isinstance(animation_data, dict) and not animation_data.get("fallback", False):
            # Successful animation generation
            confidence_score = min(0.98, confidence_score + 0.05)
        elif isinstance(animation_data, dict) and animation_data.get("fallback", False):
            # Fallback mode
            confidence_score = max(0.75, confidence_score - 0.15)
        
        result = ISLOutput(
            source_text=transcribed_text,
            isl_gloss=isl_gloss,
            avatar_stream_url=avatar_stream_url,
            confidence=confidence_score,
            processing_time_ms=processing_time
        )
        
        logger.info(f"Translation completed in {processing_time}ms: {transcribed_text} -> {isl_gloss}")
        
        return result
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=f"Input validation failed: {str(ve)}")
    
    except Exception as e:
        logger.error(f"Translation processing error: {str(e)}")
        app_state["service_status"] = "degraded"
        raise HTTPException(status_code=500, detail=f"Translation service error: {str(e)}")


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "NOT_FOUND",
                "message": "The requested endpoint was not found",
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url.path)
            }
        }
    )


@app.websocket("/avatar/stream/{stream_id}")
async def avatar_websocket_endpoint(websocket: WebSocket, stream_id: str):
    """
    WebSocket endpoint for streaming avatar animations
    
    Args:
        websocket: WebSocket connection
        stream_id: Unique identifier for the animation stream
    """
    logger.info(f"WebSocket connection request for avatar stream: {stream_id}")
    await handle_avatar_websocket(websocket, stream_id)


@app.get("/avatar/stats")
async def get_avatar_stream_stats():
    """Get statistics about active avatar streams"""
    stats = avatar_stream_manager.get_stream_stats()
    return {
        "status": "success",
        "data": stats,
        "timestamp": datetime.now()
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR", 
                "message": "An internal server error occurred",
                "timestamp": datetime.now().isoformat()
            }
        }
    )


@app.on_event("startup")
async def startup_event():
    """Application startup event handler"""
    logger.info("Starting Voice-to-ISL Translation API...")
    
    # Start background cleanup task
    asyncio.create_task(cleanup_expired_streams_task())
    
    logger.info("Avatar stream cleanup task started")
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler"""
    logger.info("Shutting down Voice-to-ISL Translation API...")
    
    # Close all active WebSocket connections
    active_connections = avatar_stream_manager.get_active_connections_count()
    if active_connections > 0:
        logger.info(f"Closing {active_connections} active WebSocket connections...")
        # WebSocket connections will be closed automatically when the server shuts down
    
    logger.info("Application shutdown complete")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
