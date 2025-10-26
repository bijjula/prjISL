/**
 * VoiceToISL React Component
 * Real-time Bidirectional Voice-to-ISL & ISL-to-Voice Translation System
 * 
 * This component simulates the L1 Client Layer (Recipient/Speaker Mobile App UI),
 * handling user input and displaying the Voice-to-ISL translation workflow
 * in a responsive four-quadrant layout.
 */

import React, { useState, useEffect } from 'react';
import './VoiceToISL.css';

// TypeScript interfaces for API communication
interface VoiceInput {
  audio_text: string;
}

interface ISLOutput {
  source_text: string;
  isl_gloss: string;
  avatar_stream_url: string;
  confidence: number;
  processing_time_ms: number;
}

interface AnimationFrame {
  frame_number: number;
  timestamp: number;
  duration: number;
  joint_positions: Record<string, [number, number, number]>;
  interpolation: string;
}

interface AnimationData {
  total_duration: number;
  frame_count: number;
  fps: number;
  resolution: string;
  gloss_input: string;
  parsed_words: string[];
}

interface WebSocketMessage {
  type: 'animation_metadata' | 'animation_frame' | 'animation_complete' | 'error' | 'ping' | 'pong';
  stream_id: string;
  data?: any;
  error?: {
    code: string;
    message: string;
    timestamp: number;
  };
  timestamp: number;
}

interface ApiError {
  error: {
    code: string;
    message: string;
    details?: any;
    timestamp: string;
    trace_id?: string;
  };
}

interface TranslationState {
  isLoading: boolean;
  result: ISLOutput | null;
  error: string | null;
}

interface AvatarAnimationState {
  isConnected: boolean;
  isPlaying: boolean;
  animationData: AnimationData | null;
  currentFrame: AnimationFrame | null;
  progress: number;
  error: string | null;
  videoFrames: VideoFrame[];
  currentFrameIndex: number;
}

interface VideoFrame {
  frame_number: number;
  timestamp: number;
  duration: number;
  visual_frame: {
    type: string;
    data_url: string;
    width: number;
    height: number;
    svg_content: string;
  };
}

/**
 * Main VoiceToISL functional component
 * 
 * Implements the four-quadrant user interface:
 * - Top-Left: Voice Recording/Input Simulation
 * - Bottom-Left: Text Tokens (Transcribed Text)
 * - Top-Right: ISL Gloss Display
 * - Bottom-Right: Avatar Rendering Placeholder
 */
const VoiceToISL: React.FC = () => {
  // Component state management
  const [inputText, setInputText] = useState<string>('');
  const [translationState, setTranslationState] = useState<TranslationState>({
    isLoading: false,
    result: null,
    error: null
  });
  const [apiHealth, setApiHealth] = useState<'checking' | 'healthy' | 'error'>('checking');
  const [avatarState, setAvatarState] = useState<AvatarAnimationState>({
    isConnected: false,
    isPlaying: false,
    animationData: null,
    currentFrame: null,
    progress: 0,
    error: null,
    videoFrames: [],
    currentFrameIndex: 0
  });

  // WebSocket reference for avatar animation streaming
  const [avatarWebSocket, setAvatarWebSocket] = useState<WebSocket | null>(null);
  
  // Animation playback control
  const [animationTimer, setAnimationTimer] = useState<NodeJS.Timeout | null>(null);

  // API configuration
  const API_BASE_URL = 'http://localhost:8000';
  const TRANSLATION_ENDPOINT = `${API_BASE_URL}/api/v1/translate/voice-to-isl`;
  const HEALTH_ENDPOINT = `${API_BASE_URL}/health`;
  const WEBSOCKET_BASE_URL = 'ws://localhost:8000';

  /**
   * Check API health status on component mount and cleanup WebSocket on unmount
   */
  useEffect(() => {
    checkApiHealth();

    // Cleanup function
    return () => {
      if (avatarWebSocket) {
        avatarWebSocket.close();
      }
      if (animationTimer) {
        clearTimeout(animationTimer);
      }
    };
  }, [avatarWebSocket]);

  /**
   * Health check function to verify backend connectivity
   */
  const checkApiHealth = async (): Promise<void> => {
    try {
      const response = await fetch(HEALTH_ENDPOINT, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setApiHealth('healthy');
      } else {
        setApiHealth('error');
      }
    } catch (error) {
      console.error('API health check failed:', error);
      setApiHealth('error');
    }
  };

  /**
   * Main translation function that calls the FastAPI backend
   * 
   * @param audioText - The simulated voice input text
   */
  const handleTranslation = async (): Promise<void> => {
    // Input validation
    if (!inputText.trim()) {
      setTranslationState({
        isLoading: false,
        result: null,
        error: 'Please enter some text to translate'
      });
      return;
    }

    // Reset state and start loading
    setTranslationState({
      isLoading: true,
      result: null,
      error: null
    });

    try {
      const requestPayload: VoiceInput = {
        audio_text: inputText.trim()
      };

      const response = await fetch(TRANSLATION_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestPayload),
      });

      if (!response.ok) {
        // Handle API errors
        const errorData: ApiError = await response.json();
        throw new Error(errorData.error.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result: ISLOutput = await response.json();
      
      setTranslationState({
        isLoading: false,
        result: result,
        error: null
      });

      // Connect to WebSocket for avatar animation if stream URL is provided
      if (result.avatar_stream_url && result.avatar_stream_url.startsWith('ws://')) {
        connectToAvatarStream(result.avatar_stream_url);
      }

    } catch (error) {
      console.error('Translation error:', error);
      setTranslationState({
        isLoading: false,
        result: null,
        error: error instanceof Error ? error.message : 'An unexpected error occurred'
      });
    }
  };

  /**
   * Handle Enter key press for form submission
   */
  const handleKeyPress = (event: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleTranslation();
    }
  };

  /**
   * Clear all results and reset form
   */
  const handleClear = (): void => {
    setInputText('');
    setTranslationState({
      isLoading: false,
      result: null,
      error: null
    });
  };

  /**
   * Sample text suggestions for quick testing
   */
  const sampleTexts = [
    "Hello, how are you?",
    "Good morning, nice to meet you",
    "Thank you for your help",
    "Where is the hospital?",
    "My name is John"
  ];

  const handleSampleText = (text: string): void => {
    setInputText(text);
  };

  /**
   * Connect to WebSocket for avatar animation streaming
   */
  const connectToAvatarStream = (streamUrl: string): void => {
    // Close existing connection if any
    if (avatarWebSocket) {
      avatarWebSocket.close();
    }

    // Reset avatar state
    setAvatarState({
      isConnected: false,
      isPlaying: false,
      animationData: null,
      currentFrame: null,
      progress: 0,
      error: null,
      videoFrames: [],
      currentFrameIndex: 0
    });

    try {
      const ws = new WebSocket(streamUrl);
      
      ws.onopen = () => {
        console.log('Avatar WebSocket connected:', streamUrl);
        setAvatarState(prev => ({
          ...prev,
          isConnected: true,
          error: null
        }));
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          handleWebSocketMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('Avatar WebSocket error:', error);
        setAvatarState(prev => ({
          ...prev,
          error: 'WebSocket connection error',
          isConnected: false
        }));
      };

      ws.onclose = () => {
        console.log('Avatar WebSocket disconnected');
        setAvatarState(prev => ({
          ...prev,
          isConnected: false,
          isPlaying: false
        }));
      };

      setAvatarWebSocket(ws);

    } catch (error) {
      console.error('Failed to connect to avatar stream:', error);
      setAvatarState(prev => ({
        ...prev,
        error: 'Failed to connect to animation stream'
      }));
    }
  };

  /**
   * Start controlled animation playback with proper timing
   */
  const startControlledPlayback = (frames: VideoFrame[]): void => {
    if (frames.length === 0) return;
    
    // Clear any existing timer
    if (animationTimer) {
      clearTimeout(animationTimer);
    }
    
    let currentIndex = 0;
    
    const playNextFrame = () => {
      if (currentIndex >= frames.length) {
        // Animation complete
        setAvatarState(prev => ({
          ...prev,
          isPlaying: false,
          progress: 100
        }));
        return;
      }
      
      const currentFrame = frames[currentIndex];
      
      setAvatarState(prev => ({
        ...prev,
        currentFrameIndex: currentIndex,
        progress: prev.animationData 
          ? ((currentIndex + 1) / frames.length) * 100 
          : 0
      }));
      
      currentIndex++;
      
      // Use frame duration (convert to milliseconds) for timing
      // Each frame should be displayed for its duration
      const frameDisplayTime = currentFrame.duration * 1000; // Convert seconds to milliseconds
      
      const timer = setTimeout(playNextFrame, frameDisplayTime);
      setAnimationTimer(timer);
    };
    
    // Start playback
    playNextFrame();
  };

  /**
   * Handle incoming WebSocket messages
   */
  const handleWebSocketMessage = (message: WebSocketMessage): void => {
    switch (message.type) {
      case 'animation_metadata':
        console.log('Received animation metadata:', message.data);
        setAvatarState(prev => ({
          ...prev,
          animationData: message.data,
          isPlaying: true,
          progress: 0,
          videoFrames: [],
          currentFrameIndex: 0
        }));
        break;

      case 'animation_frame':
        console.log('Received animation frame:', message.data.frame_number);
        const frameData = message.data as VideoFrame;
        
        setAvatarState(prev => {
          const newFrames = [...prev.videoFrames, frameData];
          return {
            ...prev,
            currentFrame: message.data,
            videoFrames: newFrames
          };
        });
        break;

      case 'animation_complete':
        console.log('Animation playbook complete, starting controlled playback');
        setAvatarState(prev => {
          // Start controlled playback when all frames are received
          if (prev.videoFrames.length > 0) {
            startControlledPlayback(prev.videoFrames);
          }
          return {
            ...prev,
            progress: 0
          };
        });
        break;

      case 'error':
        console.error('WebSocket error:', message.error);
        setAvatarState(prev => ({
          ...prev,
          error: message.error?.message || 'Animation error',
          isPlaying: false
        }));
        break;

      case 'ping':
        // Respond to server ping with pong
        if (avatarWebSocket) {
          avatarWebSocket.send(JSON.stringify({
            type: 'pong',
            timestamp: Date.now() / 1000
          }));
        }
        break;

      default:
        console.log('Unknown WebSocket message type:', message.type);
    }
  };

  /**
   * Restart avatar animation
   */
  const restartAnimation = (): void => {
    if (avatarWebSocket && avatarWebSocket.readyState === WebSocket.OPEN) {
      avatarWebSocket.send(JSON.stringify({
        type: 'restart_animation',
        timestamp: Date.now() / 1000
      }));
    }
  };

  return (
    <div className="voice-to-isl-container">
      {/* Header Section */}
      <header className="app-header">
        <h1>Voice-to-ISL Translation System</h1>
        <div className="api-status">
          <span className={`status-indicator ${apiHealth}`}>
            {apiHealth === 'checking' && '🔄 Checking API...'}
            {apiHealth === 'healthy' && '✅ API Connected'}
            {apiHealth === 'error' && '❌ API Disconnected'}
          </span>
        </div>
      </header>

      {/* Input Section */}
      <section className="input-section">
        <div className="input-group">
          <label htmlFor="voice-input">Enter text to simulate voice input:</label>
          <textarea
            id="voice-input"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here... (Press Enter to translate)"
            rows={3}
            maxLength={1000}
            disabled={translationState.isLoading}
          />
          <div className="character-count">
            {inputText.length}/1000 characters
          </div>
        </div>

        <div className="action-buttons">
          <button
            onClick={handleTranslation}
            disabled={translationState.isLoading || !inputText.trim()}
            className="translate-btn primary"
          >
            {translationState.isLoading ? '🔄 Translating...' : '🎤 Translate to ISL'}
          </button>
          <button
            onClick={handleClear}
            disabled={translationState.isLoading}
            className="clear-btn secondary"
          >
            🗑️ Clear
          </button>
        </div>

        {/* Sample Text Buttons */}
        <div className="sample-texts">
          <span>Quick samples:</span>
          {sampleTexts.map((text, index) => (
            <button
              key={index}
              onClick={() => handleSampleText(text)}
              className="sample-btn"
              disabled={translationState.isLoading}
            >
              {text}
            </button>
          ))}
        </div>
      </section>

      {/* Four-Quadrant Display Section */}
      <section className="quadrant-container">
        {/* Top-Left Quadrant: Voice Recording Simulation */}
        <div className="quadrant top-left">
          <div className="quadrant-header">
            <h3>📻 Voice Input Recording</h3>
            <span className="quadrant-description">Simulated voice capture</span>
          </div>
          <div className="quadrant-content">
            <div className="voice-simulation">
              <div className={`voice-indicator ${translationState.isLoading ? 'active' : ''}`}>
                🎤
              </div>
              <p className="simulation-text">
                {translationState.isLoading
                  ? 'Recording voice input...'
                  : inputText
                    ? 'Voice input ready for processing'
                    : 'No voice input detected'
                }
              </p>
            </div>
          </div>
        </div>

        {/* Top-Right Quadrant: ISL Gloss Display */}
        <div className="quadrant top-right">
          <div className="quadrant-header">
            <h3>📝 ISL Gloss Notation</h3>
            <span className="quadrant-description">Linguistic representation</span>
          </div>
          <div className="quadrant-content">
            <div className="gloss-display">
              {translationState.result ? (
                <>
                  <div className="gloss-text">
                    {translationState.result.isl_gloss}
                  </div>
                  <div className="confidence-score">
                    Confidence: {(translationState.result.confidence * 100).toFixed(1)}%
                  </div>
                </>
              ) : translationState.error ? (
                <div className="error-message">
                  ❌ {translationState.error}
                </div>
              ) : (
                <div className="placeholder-text">
                  ISL gloss notation will appear here
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Bottom-Left Quadrant: Text Tokens */}
        <div className="quadrant bottom-left">
          <div className="quadrant-header">
            <h3>📄 Transcribed Text</h3>
            <span className="quadrant-description">ASR output tokens</span>
          </div>
          <div className="quadrant-content">
            <div className="text-tokens">
              {translationState.result ? (
                <div className="token-text">
                  {translationState.result.source_text}
                </div>
              ) : translationState.isLoading ? (
                <div className="loading-text">
                  🔄 Processing speech recognition...
                </div>
              ) : (
                <div className="placeholder-text">
                  Transcribed text will appear here
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Bottom-Right Quadrant: Avatar Rendering */}
        <div className="quadrant bottom-right">
          <div className="quadrant-header">
            <h3>🤖 3D Avatar Animation</h3>
            <span className="quadrant-description">ISL sign rendering</span>
          </div>
          <div className="quadrant-content">
          <div className="avatar-container">
            {translationState.result ? (
              <>
                <div className="avatar-display">
                  {avatarState.videoFrames.length > 0 && avatarState.currentFrameIndex < avatarState.videoFrames.length ? (
                    <div className="avatar-video-player">
                      <div className="video-frame">
                        {avatarState.videoFrames[avatarState.currentFrameIndex]?.visual_frame?.data_url ? (
                          <img 
                            src={avatarState.videoFrames[avatarState.currentFrameIndex].visual_frame.data_url}
                            alt={`Avatar animation frame ${avatarState.currentFrameIndex}`}
                            className="avatar-frame-image"
                            style={{
                              width: '100%',
                              height: 'auto',
                              maxHeight: '300px',
                              borderRadius: '8px',
                              border: '2px solid #ddd'
                            }}
                          />
                        ) : (
                          <div className="frame-loading">Loading frame...</div>
                        )}
                      </div>
                      <div className="video-info">
                        <div className="frame-info">
                          Frame {avatarState.currentFrameIndex + 1} of {avatarState.videoFrames.length}
                        </div>
                        <div className="signing-text">
                          {avatarState.isPlaying ? 'Signing:' : 'Signed:'} {translationState.result.isl_gloss}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className={`avatar-placeholder ${avatarState.isPlaying ? 'playing' : ''}`}>
                      🧑‍🦽
                      <div className="avatar-animation">
                        {avatarState.isPlaying ? 'Loading animation...' : 'Ready to sign'}
                      </div>
                      {avatarState.currentFrame && (
                        <div className="frame-info">
                          Frame {avatarState.currentFrame.frame_number}
                          {avatarState.animationData && ` of ${avatarState.animationData.frame_count}`}
                        </div>
                      )}
                    </div>
                  )}
                  
                  <div className="animation-controls">
                    <div className="connection-status">
                      <span className={`status-dot ${avatarState.isConnected ? 'connected' : 'disconnected'}`}></span>
                      {avatarState.isConnected ? 'Connected' : 'Disconnected'}
                    </div>
                    
                    {avatarState.animationData && (
                      <div className="animation-info">
                        <div className="progress-bar">
                          <div 
                            className="progress-fill" 
                            style={{ width: `${avatarState.progress}%` }}
                          ></div>
                        </div>
                        <div className="animation-stats">
                          Duration: {avatarState.animationData.total_duration}s | 
                          FPS: {avatarState.animationData.fps} | 
                          Frames: {avatarState.animationData.frame_count}
                        </div>
                      </div>
                    )}
                    
                    {avatarState.isConnected && !avatarState.isPlaying && (
                      <button 
                        onClick={restartAnimation}
                        className="restart-btn"
                      >
                        🔄 Replay Animation
                      </button>
                    )}
                  </div>
                </div>
                
                <div className="stream-info">
                  <strong>Stream ID:</strong>
                  <code>{translationState.result.avatar_stream_url.split('/').pop()}</code>
                </div>
                
                <div className="processing-time">
                  Processed in: {translationState.result.processing_time_ms}ms
                </div>
                
                {avatarState.error && (
                  <div className="avatar-error">
                    ⚠️ {avatarState.error}
                  </div>
                )}
              </>
            ) : translationState.isLoading ? (
              <div className="loading-avatar">
                <div className="spinner">🔄</div>
                <div>Generating avatar animation...</div>
              </div>
            ) : (
              <div className="placeholder-text">
                <div className="avatar-placeholder-icon">🤖</div>
                <div>3D avatar will appear here</div>
              </div>
            )}
          </div>
          </div>
        </div>
      </section>

      {/* Footer with Technical Information */}
      <footer className="app-footer">
        <div className="technical-info">
          <span>💡 MVS Demo: Simulating L4 Core Data Plane Services</span>
          <span>🔧 Tech Stack: React + TypeScript + FastAPI + Python</span>
          <span>🎯 Translation Pipeline: ASR → NLP → Animation Engine</span>
        </div>
      </footer>
    </div>
  );
};

export default VoiceToISL;
