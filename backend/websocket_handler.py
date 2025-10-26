#!/usr/bin/env python3
"""
WebSocket Handler for Avatar Animation Streaming
Real-time Bidirectional Voice-to-ISL & ISL-to-Voice Translation System

This module handles WebSocket connections for streaming real-time avatar animation data.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
import json
import logging
import asyncio
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class AvatarStreamManager:
    """Manages WebSocket connections for avatar animation streaming"""
    
    def __init__(self):
        # Active WebSocket connections: {stream_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Animation data cache: {stream_id: animation_data}
        self.animation_cache: Dict[str, Dict] = {}
        
        # Connection metadata: {stream_id: metadata}
        self.connection_metadata: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, stream_id: str):
        """Accept a new WebSocket connection for avatar streaming"""
        await websocket.accept()
        
        self.active_connections[stream_id] = websocket
        self.connection_metadata[stream_id] = {
            "connected_at": datetime.now(),
            "client_ip": websocket.client.host if websocket.client else "unknown",
            "frames_sent": 0,
            "last_activity": datetime.now()
        }
        
        logger.info(f"Avatar stream connected: {stream_id} from {websocket.client.host if websocket.client else 'unknown'}")
    
    def disconnect(self, stream_id: str):
        """Handle WebSocket disconnection"""
        if stream_id in self.active_connections:
            del self.active_connections[stream_id]
        
        if stream_id in self.connection_metadata:
            metadata = self.connection_metadata[stream_id]
            duration = (datetime.now() - metadata["connected_at"]).total_seconds()
            logger.info(f"Avatar stream disconnected: {stream_id}, duration: {duration:.2f}s, frames sent: {metadata['frames_sent']}")
            del self.connection_metadata[stream_id]
        
        # Keep animation cache for a while in case of reconnection
        # It will be cleaned up by cleanup_expired_streams()
    
    def store_animation_data(self, stream_id: str, animation_data: Dict):
        """Store animation data for a stream"""
        self.animation_cache[stream_id] = {
            **animation_data,
            "cached_at": time.time()
        }
        logger.info(f"Cached animation data for stream: {stream_id}")
    
    async def send_animation_frame(self, stream_id: str, frame_data: Dict):
        """Send a single animation frame to the connected client"""
        if stream_id not in self.active_connections:
            logger.warning(f"Attempted to send frame to disconnected stream: {stream_id}")
            return False
        
        websocket = self.active_connections[stream_id]
        
        try:
            await websocket.send_text(json.dumps(frame_data))
            
            # Update metadata
            if stream_id in self.connection_metadata:
                self.connection_metadata[stream_id]["frames_sent"] += 1
                self.connection_metadata[stream_id]["last_activity"] = datetime.now()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send frame to {stream_id}: {str(e)}")
            self.disconnect(stream_id)
            return False
    
    async def stream_animation(self, stream_id: str):
        """Stream complete animation sequence to connected client"""
        if stream_id not in self.animation_cache:
            logger.error(f"No animation data found for stream: {stream_id}")
            await self.send_error(stream_id, "ANIMATION_NOT_FOUND", "Animation data not available")
            return
        
        if stream_id not in self.active_connections:
            logger.warning(f"No active connection for stream: {stream_id}")
            return
        
        animation_data = self.animation_cache[stream_id]
        
        try:
            # Send animation metadata first
            metadata_message = {
                "type": "animation_metadata",
                "stream_id": stream_id,
                "data": {
                    "total_duration": animation_data.get("total_duration_seconds", 0),
                    "frame_count": animation_data.get("frame_count", 0),
                    "fps": animation_data.get("fps", 30),
                    "resolution": animation_data.get("resolution", "400x600"),
                    "gloss_input": animation_data.get("gloss_input", ""),
                    "parsed_words": animation_data.get("parsed_words", [])
                },
                "timestamp": time.time()
            }
            
            if not await self.send_animation_frame(stream_id, metadata_message):
                return
            
            # Decode and stream animation frames
            video_data_base64 = animation_data.get("video_data_base64", "")
            if video_data_base64:
                import base64
                
                try:
                    # Decode base64 animation data
                    decoded_data = base64.b64decode(video_data_base64)
                    animation_json = json.loads(decoded_data.decode('utf-8'))
                    
                    frames = animation_json.get("frames", [])
                    fps = animation_json.get("fps", 30)
                    frame_duration = 1.0 / fps
                    
                    logger.info(f"Streaming {len(frames)} frames for {stream_id} at {fps} FPS")
                    
                    # Stream frames with proper timing
                    for frame in frames:
                        frame_message = {
                            "type": "animation_frame",
                            "stream_id": stream_id,
                            "data": frame,
                            "timestamp": time.time()
                        }
                        
                        if not await self.send_animation_frame(stream_id, frame_message):
                            break
                        
                        # Wait for next frame (simulate real-time playback)
                        await asyncio.sleep(frame_duration)
                    
                    # Send completion message
                    completion_message = {
                        "type": "animation_complete",
                        "stream_id": stream_id,
                        "data": {
                            "frames_sent": len(frames),
                            "total_duration": animation_data.get("total_duration_seconds", 0)
                        },
                        "timestamp": time.time()
                    }
                    
                    await self.send_animation_frame(stream_id, completion_message)
                    
                except Exception as e:
                    logger.error(f"Failed to decode animation data for {stream_id}: {str(e)}")
                    await self.send_error(stream_id, "DECODE_ERROR", "Failed to decode animation data")
            
            else:
                await self.send_error(stream_id, "NO_ANIMATION_DATA", "No animation frames available")
        
        except Exception as e:
            logger.error(f"Animation streaming failed for {stream_id}: {str(e)}")
            await self.send_error(stream_id, "STREAMING_ERROR", str(e))
    
    async def send_error(self, stream_id: str, error_code: str, error_message: str):
        """Send error message to client"""
        error_frame = {
            "type": "error",
            "stream_id": stream_id,
            "error": {
                "code": error_code,
                "message": error_message,
                "timestamp": time.time()
            }
        }
        
        await self.send_animation_frame(stream_id, error_frame)
    
    def cleanup_expired_streams(self, max_age_seconds: int = 3600):
        """Clean up expired animation cache entries"""
        current_time = time.time()
        expired_streams = []
        
        for stream_id, data in self.animation_cache.items():
            if current_time - data.get("cached_at", 0) > max_age_seconds:
                expired_streams.append(stream_id)
        
        for stream_id in expired_streams:
            del self.animation_cache[stream_id]
            logger.info(f"Cleaned up expired animation cache for: {stream_id}")
    
    def get_active_connections_count(self) -> int:
        """Get count of active WebSocket connections"""
        return len(self.active_connections)
    
    def get_stream_stats(self) -> Dict:
        """Get statistics about active streams"""
        return {
            "active_connections": len(self.active_connections),
            "cached_animations": len(self.animation_cache),
            "total_frames_sent": sum(
                metadata.get("frames_sent", 0) 
                for metadata in self.connection_metadata.values()
            ),
            "connections": [
                {
                    "stream_id": stream_id,
                    "connected_at": metadata["connected_at"].isoformat(),
                    "frames_sent": metadata["frames_sent"],
                    "client_ip": metadata["client_ip"]
                }
                for stream_id, metadata in self.connection_metadata.items()
            ]
        }

# Global stream manager instance
avatar_stream_manager = AvatarStreamManager()

async def handle_avatar_websocket(websocket: WebSocket, stream_id: str):
    """
    Main WebSocket handler for avatar animation streaming
    
    Args:
        websocket: FastAPI WebSocket connection
        stream_id: Unique identifier for the animation stream
    """
    await avatar_stream_manager.connect(websocket, stream_id)
    
    try:
        # Start streaming animation if data is available
        await avatar_stream_manager.stream_animation(stream_id)
        
        # Keep connection alive and handle client messages
        while True:
            try:
                # Wait for client messages (with timeout)
                message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                try:
                    data = json.loads(message)
                    message_type = data.get("type", "unknown")
                    
                    if message_type == "ping":
                        # Respond to ping with pong
                        pong_response = {
                            "type": "pong",
                            "timestamp": time.time()
                        }
                        await avatar_stream_manager.send_animation_frame(stream_id, pong_response)
                    
                    elif message_type == "restart_animation":
                        # Restart animation playback
                        await avatar_stream_manager.stream_animation(stream_id)
                    
                    elif message_type == "get_stats":
                        # Send stream statistics
                        stats_response = {
                            "type": "stats",
                            "data": avatar_stream_manager.get_stream_stats(),
                            "timestamp": time.time()
                        }
                        await avatar_stream_manager.send_animation_frame(stream_id, stats_response)
                    
                    else:
                        logger.warning(f"Unknown message type from {stream_id}: {message_type}")
                
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received from {stream_id}: {message}")
            
            except asyncio.TimeoutError:
                # Send keepalive ping
                ping_message = {
                    "type": "ping",
                    "timestamp": time.time()
                }
                if not await avatar_stream_manager.send_animation_frame(stream_id, ping_message):
                    break
            
            except WebSocketDisconnect:
                break
    
    except WebSocketDisconnect:
        pass
    
    except Exception as e:
        logger.error(f"WebSocket error for {stream_id}: {str(e)}")
    
    finally:
        avatar_stream_manager.disconnect(stream_id)

# Cleanup task that runs periodically
async def cleanup_expired_streams_task():
    """Background task to cleanup expired animation cache"""
    while True:
        try:
            avatar_stream_manager.cleanup_expired_streams()
            await asyncio.sleep(300)  # Run every 5 minutes
        except Exception as e:
            logger.error(f"Cleanup task error: {str(e)}")
            await asyncio.sleep(60)  # Retry after 1 minute on error
