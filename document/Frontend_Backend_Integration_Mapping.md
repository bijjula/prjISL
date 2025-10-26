# Frontend-Backend Integration Mapping
## Real-time Bidirectional Voice-to-ISL & ISL-to-Voice Translation System

| Document Information | Details |
|---------------------|---------|
| **Document Version** | v1.0 |
| **Date** | October 25, 2024 |
| **Purpose** | Define integration mappings between React frontend and FastAPI backend |
| **Technology Stack** | React 18+ with TypeScript, FastAPI with Python 3.9+ |

---

## 1. Architecture Overview

### 1.1 Communication Protocols

| Protocol | Usage | Components |
|----------|-------|------------|
| **HTTP/REST** | API calls for CRUD operations | Authentication, User Management, Friends, Conversations |
| **WebSocket** | Real-time bidirectional communication | Translation streams, Conversation events |
| **WebRTC** | Audio/video streaming | Voice recording, Video capture, Media transmission |

### 1.2 Data Flow Summary

```
Frontend React Components → API Service Layer → FastAPI Endpoints → Business Logic → Database
                         ↑                                        ↓
WebSocket Client ←→ WebSocket Server ←→ Translation Services → Message Queue
```

---

## 2. Component-to-API Mapping

### 2.1 Authentication Components

#### Login Component (`src/components/auth/LoginForm.tsx`)

**API Integration:**
```typescript
// POST /api/v1/auth/login
interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  success: boolean;
  data: {
    accessToken: string;
    refreshToken: string;
    expiresIn: number;
    userProfile: UserProfile;
  };
}

// Usage in component
const handleLogin = async (credentials: LoginRequest) => {
  const response = await authAPI.login(credentials);
  // Store tokens in secure storage
  tokenStorage.setTokens(response.data.accessToken, response.data.refreshToken);
  // Update user context
  setUser(response.data.userProfile);
};
```

**Backend Handler:**
```python
# backend/src/api/auth.py
@router.post("/login", response_model=AuthResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return AuthResponse(
        success=True,
        data=AuthData(
            accessToken=access_token,
            refreshToken=refresh_token,
            expiresIn=3600,
            userProfile=UserProfile.from_orm(user)
        )
    )
```

#### Registration Component (`src/components/auth/RegisterForm.tsx`)

**API Integration:**
```typescript
// POST /api/v1/auth/register
interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  userType: 'hearing' | 'deaf' | 'admin';
  firstName: string;
  lastName: string;
  preferredLanguage: string;
  avatarSettings?: AvatarSettings;
}

const handleRegister = async (userData: RegisterRequest) => {
  try {
    const response = await authAPI.register(userData);
    // Auto-login after successful registration
    tokenStorage.setTokens(response.data.accessToken, response.data.refreshToken);
    setUser(response.data.userProfile);
    navigate('/dashboard');
  } catch (error) {
    setError(error.response.data.error.message);
  }
};
```

**Form Validation:**
```typescript
const validationSchema = yup.object({
  username: yup.string()
    .matches(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores')
    .min(3, 'Username must be at least 3 characters')
    .max(50, 'Username must be less than 50 characters')
    .required('Username is required'),
  email: yup.string()
    .email('Please enter a valid email')
    .required('Email is required'),
  password: yup.string()
    .min(8, 'Password must be at least 8 characters')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, 'Password must contain uppercase, lowercase, and number')
    .required('Password is required')
});
```

### 2.2 Translation Components

#### Four-Quadrant Layout (`src/components/translation/TranslationInterface.tsx`)

**Component Structure:**
```typescript
interface TranslationInterfaceProps {
  sessionId?: string;
  mode: 'voice-to-isl' | 'isl-to-voice' | 'bidirectional';
  onTranslationResult?: (result: TranslationResult) => void;
}

const TranslationInterface: React.FC<TranslationInterfaceProps> = ({ 
  sessionId, 
  mode, 
  onTranslationResult 
}) => {
  const [translationSession, setTranslationSession] = useState<TranslationSession | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const websocketRef = useRef<WebSocket | null>(null);

  // Initialize translation session
  useEffect(() => {
    const initializeSession = async () => {
      const response = await translationAPI.startStreamingTranslation({
        mode,
        language: 'hi',
        quality: 'high'
      });
      setTranslationSession(response.data);
      
      // Establish WebSocket connection
      const ws = new WebSocket(`${response.data.websocketUrl}?token=${getAccessToken()}`);
      websocketRef.current = ws;
      
      ws.onmessage = handleWebSocketMessage;
      ws.onerror = handleWebSocketError;
    };
    
    initializeSession();
  }, [mode]);

  return (
    <div className="translation-interface grid grid-cols-2 grid-rows-2 h-screen">
      <VoiceRecordingQuadrant 
        isRecording={isRecording}
        onAudioData={sendAudioData}
        className="border-r border-b"
      />
      <ISLGlossQuadrant 
        gloss={currentGloss}
        confidence={glossConfidence}
        className="border-b"
      />
      <TextDisplayQuadrant 
        text={transcribedText}
        confidence={textConfidence}
        className="border-r"
      />
      <AvatarRenderingQuadrant 
        poseData={avatarPoseData}
        isAnimating={isAnimating}
      />
    </div>
  );
};
```

#### Voice Recording Quadrant (`src/components/translation/VoiceRecordingQuadrant.tsx`)

**WebRTC Integration:**
```typescript
interface VoiceRecordingQuadrantProps {
  isRecording: boolean;
  onAudioData: (audioData: ArrayBuffer) => void;
  className?: string;
}

const VoiceRecordingQuadrant: React.FC<VoiceRecordingQuadrantProps> = ({
  isRecording,
  onAudioData,
  className
}) => {
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [audioLevel, setAudioLevel] = useState(0);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        }
      });

      const recorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          // Convert to ArrayBuffer and send via WebSocket
          event.data.arrayBuffer().then(onAudioData);
        }
      };

      recorder.start(100); // Send data every 100ms for real-time processing
      setMediaRecorder(recorder);
      
      // Setup audio visualization
      setupAudioVisualization(stream);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const setupAudioVisualization = (stream: MediaStream) => {
    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);
    
    analyser.fftSize = 256;
    source.connect(analyser);
    
    audioContextRef.current = audioContext;
    analyserRef.current = analyser;
    
    updateAudioLevel();
  };

  const updateAudioLevel = () => {
    if (!analyserRef.current) return;
    
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);
    
    const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
    setAudioLevel(average / 255);
    
    requestAnimationFrame(updateAudioLevel);
  };

  return (
    <div className={`voice-recording-quadrant p-4 ${className}`}>
      <div className="flex flex-col items-center justify-center h-full">
        <div className="relative">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`w-20 h-20 rounded-full ${
              isRecording ? 'bg-red-500 animate-pulse' : 'bg-blue-500'
            } text-white flex items-center justify-center text-2xl`}
          >
            {isRecording ? '⏹️' : '🎤'}
          </button>
          
          {/* Audio level visualization */}
          <div className="absolute -inset-2">
            <div 
              className="w-full h-full rounded-full border-4 border-blue-300"
              style={{
                transform: `scale(${1 + audioLevel * 0.5})`,
                opacity: audioLevel
              }}
            />
          </div>
        </div>
        
        <p className="mt-4 text-center text-gray-600">
          {isRecording ? 'Recording... Speak now' : 'Click to start recording'}
        </p>
        
        {/* Audio waveform visualization */}
        <AudioWaveform audioLevel={audioLevel} />
      </div>
    </div>
  );
};
```

#### WebSocket Message Handling

**Frontend WebSocket Service:**
```typescript
// src/services/websocket.ts
export class TranslationWebSocketService {
  private ws: WebSocket | null = null;
  private sessionId: string;
  private messageHandlers: Map<string, (data: any) => void> = new Map();

  constructor(websocketUrl: string, sessionId: string) {
    this.sessionId = sessionId;
    this.connect(websocketUrl);
  }

  private connect(url: string) {
    this.ws = new WebSocket(`${url}?token=${getAccessToken()}`);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      const handler = this.messageHandlers.get(message.type);
      if (handler) {
        handler(message);
      }
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket closed');
      // Implement reconnection logic
      setTimeout(() => this.reconnect(), 1000);
    };
  }

  public sendAudioChunk(audioData: ArrayBuffer) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const base64Data = arrayBufferToBase64(audioData);
      const message = {
        type: 'audio_chunk',
        sessionId: this.sessionId,
        data: base64Data,
        sequence: Date.now(),
        timestamp: Date.now(),
        format: 'webm',
        sampleRate: 16000
      };
      this.ws.send(JSON.stringify(message));
    }
  }

  public sendVideoFrame(videoData: ArrayBuffer) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const base64Data = arrayBufferToBase64(videoData);
      const message = {
        type: 'video_frame',
        sessionId: this.sessionId,
        data: base64Data,
        sequence: Date.now(),
        timestamp: Date.now(),
        format: 'webm',
        frameRate: 30
      };
      this.ws.send(JSON.stringify(message));
    }
  }

  public onTextToken(handler: (data: TextTokenMessage) => void) {
    this.messageHandlers.set('text_token', handler);
  }

  public onISLGloss(handler: (data: ISLGlossMessage) => void) {
    this.messageHandlers.set('isl_gloss', handler);
  }

  public onAvatarPose(handler: (data: AvatarPoseMessage) => void) {
    this.messageHandlers.set('avatar_pose', handler);
  }

  public onAudioChunk(handler: (data: AudioChunkMessage) => void) {
    this.messageHandlers.set('audio_chunk', handler);
  }
}
```

**Backend WebSocket Handler:**
```python
# backend/src/api/websocket.py
@app.websocket("/ws/translation/{session_id}")
async def translation_websocket(
    websocket: WebSocket, 
    session_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    # Authenticate user
    user = await authenticate_websocket_token(token, db)
    if not user:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Route message based on type
            if message["type"] == "audio_chunk":
                await handle_audio_chunk(websocket, message, session_id)
            elif message["type"] == "video_frame":
                await handle_video_frame(websocket, message, session_id)
            elif message["type"] == "pose_data":
                await handle_pose_data(websocket, message, session_id)
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=4000, reason="Internal error")

async def handle_audio_chunk(websocket: WebSocket, message: dict, session_id: str):
    """Process audio chunk through ASR and NLP services"""
    try:
        # Decode base64 audio data
        audio_data = base64.b64decode(message["data"])
        
        # Send to ASR service
        text_result = await asr_service.transcribe(audio_data, message.get("format", "webm"))
        
        # Send text token back to client
        await websocket.send_text(json.dumps({
            "type": "text_token",
            "sessionId": session_id,
            "text": text_result.text,
            "confidence": text_result.confidence,
            "isFinal": text_result.is_final,
            "timestamp": int(time.time() * 1000)
        }))
        
        # If final text, send to NLP for ISL translation
        if text_result.is_final:
            gloss_result = await nlp_service.text_to_gloss(text_result.text)
            
            await websocket.send_text(json.dumps({
                "type": "isl_gloss",
                "sessionId": session_id,
                "gloss": gloss_result.gloss,
                "confidence": gloss_result.confidence,
                "timestamp": int(time.time() * 1000)
            }))
            
            # Generate avatar animation
            pose_result = await animation_service.gloss_to_poses(gloss_result.gloss)
            
            await websocket.send_text(json.dumps({
                "type": "avatar_pose",
                "sessionId": session_id,
                "poseData": pose_result.pose_data,
                "timestamp": int(time.time() * 1000)
            }))
            
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "sessionId": session_id,
            "error": {
                "code": "TRANSLATION_ERROR",
                "message": str(e),
                "canRetry": True
            },
            "timestamp": int(time.time() * 1000)
        }))
```

### 2.3 Friend Management Components

#### Friends List Component (`src/components/friends/FriendsList.tsx`)

**API Integration:**
```typescript
interface FriendsListProps {
  onStartConversation?: (friendId: string) => void;
}

const FriendsList: React.FC<FriendsListProps> = ({ onStartConversation }) => {
  const [friends, setFriends] = useState<Friend[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // GET /api/v1/friends/list
  useEffect(() => {
    const fetchFriends = async () => {
      try {
        const response = await friendsAPI.getFriendsList({
          status: 'all',
          limit: 50
        });
        setFriends(response.data.friends);
      } catch (error) {
        console.error('Error fetching friends:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFriends();
  }, []);

  const handleRemoveFriend = async (friendId: string) => {
    try {
      await friendsAPI.removeFriend(friendId);
      setFriends(friends.filter(friend => friend.userId !== friendId));
    } catch (error) {
      console.error('Error removing friend:', error);
    }
  };

  const filteredFriends = friends.filter(friend =>
    friend.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
    `${friend.firstName} ${friend.lastName}`.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="friends-list p-4">
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search friends..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-3 py-2 border rounded-lg"
        />
      </div>

      {loading ? (
        <div className="flex justify-center">
          <Spinner />
        </div>
      ) : (
        <div className="space-y-2">
          {filteredFriends.map(friend => (
            <FriendCard
              key={friend.userId}
              friend={friend}
              onStartConversation={() => onStartConversation?.(friend.userId)}
              onRemove={() => handleRemoveFriend(friend.userId)}
            />
          ))}
        </div>
      )}
    </div>
  );
};
```

### 2.4 Conversation Components

#### Conversation Manager (`src/components/conversation/ConversationManager.tsx`)

**API Integration:**
```typescript
interface ConversationManagerProps {
  friendId: string;
  onEnd?: () => void;
}

const ConversationManager: React.FC<ConversationManagerProps> = ({ friendId, onEnd }) => {
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [isConnecting, setIsConnecting] = useState(true);
  const conversationWS = useRef<WebSocket | null>(null);

  // POST /api/v1/conversations/start
  useEffect(() => {
    const startConversation = async () => {
      try {
        const response = await conversationAPI.startConversation({
          participantIds: [friendId],
          translationMode: 'bidirectional',
          language: 'hi',
          recordConversation: false
        });
        
        setConversation(response.data);
        
        // Connect to conversation WebSocket
        const ws = new WebSocket(`${response.data.websocketUrl}?token=${getAccessToken()}`);
        conversationWS.current = ws;
        
        ws.onopen = () => {
          setIsConnecting(false);
        };
        
        ws.onmessage = (event) => {
          const message = JSON.parse(event.data);
          handleConversationMessage(message);
        };
        
        ws.onclose = () => {
          setIsConnecting(true);
        };
        
      } catch (error) {
        console.error('Error starting conversation:', error);
      }
    };

    startConversation();
    
    return () => {
      // Cleanup WebSocket connection
      if (conversationWS.current) {
        conversationWS.current.close();
      }
    };
  }, [friendId]);

  const handleConversationMessage = (message: ConversationMessage) => {
    switch (message.type) {
      case 'participant_joined':
        console.log('Participant joined:', message.participant);
        break;
      case 'participant_left':
        console.log('Participant left:', message.participant);
        break;
      case 'conversation_ended':
        console.log('Conversation ended');
        onEnd?.();
        break;
    }
  };

  const endConversation = async () => {
    if (conversation) {
      try {
        await conversationAPI.endConversation(conversation.conversationId);
        onEnd?.();
      } catch (error) {
        console.error('Error ending conversation:', error);
      }
    }
  };

  if (isConnecting) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <Spinner size="large" />
          <p className="mt-4 text-gray-600">Connecting to conversation...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="conversation-manager h-screen flex flex-col">
      <ConversationHeader 
        conversation={conversation}
        onEnd={endConversation}
      />
      <TranslationInterface 
        mode="bidirectional"
        sessionId={conversation?.conversationId}
      />
    </div>
  );
};
```

---

## 3. State Management Integration

### 3.1 Redux Store Structure

```typescript
// src/store/index.ts
export interface RootState {
  auth: AuthState;
  user: UserState;
  friends: FriendsState;
  translation: TranslationState;
  conversation: ConversationState;
  ui: UIState;
}

// Auth State
interface AuthState {
  isAuthenticated: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  tokenExpiry: number | null;
  isLoading: boolean;
  error: string | null;
}

// Translation State
interface TranslationState {
  currentSession: TranslationSession | null;
  isRecording: boolean;
  isTranslating: boolean;
  currentText: string;
  currentGloss: string;
  avatarPoseData: AvatarPose | null;
  confidence: {
    asr: number;
    translation: number;
    overall: number;
  };
  error: string | null;
}
```

### 3.2 API Service Layer

```typescript
// src/services/api/index.ts
class APIService {
  private baseURL = process.env.REACT_APP_API_BASE_URL || 'https://api.isl-translator.com';
  private axiosInstance: AxiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
    });

    // Request interceptor for adding auth token
    this.axiosInstance.interceptors.request.use(
      (config) => {
        const token = tokenStorage.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for handling token refresh
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          try {
            const refreshToken = tokenStorage.getRefreshToken();
            if (refreshToken) {
              const response = await this.refreshAccessToken(refreshToken);
              tokenStorage.setTokens(response.data.accessToken, response.data.refreshToken);
              
              // Retry original request
              error.config.headers.Authorization = `Bearer ${response.data.accessToken}`;
              return this.axiosInstance.request(error.config);
            }
          } catch (refreshError) {
            // Refresh failed, redirect to login
            tokenStorage.clearTokens();
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth methods
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await this.axiosInstance.post('/api/v1/auth/login', credentials);
    return response.data;
  }

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await this.axiosInstance.post('/api/v1/auth/register', userData);
    return response.data;
  }

  // Translation methods
  async startStreamingTranslation(config: StreamConfig): Promise<StreamSessionResponse> {
    const response = await this.axiosInstance.post('/api/v1/translate/stream/start', config);
    return response.data;
  }

  async voiceToISLTranslation(data: VoiceInput): Promise<ISLOutput> {
    const response = await this.axiosInstance.post('/api/v1/translate/voice-to-isl', data);
    return response.data;
  }

  // Friends methods
  async getFriendsList(params: FriendsListParams): Promise<FriendsListResponse> {
    const response = await this.axiosInstance.get('/api/v1/friends/list', { params });
    return response.data;
  }

  async sendFriendRequest(data: FriendRequestData): Promise<FriendRequestResponse> {
    const response = await this.axiosInstance.post('/api/v1/friends/request', data);
    return response.data;
  }
}

export const apiService = new APIService();
```

---

## 4. Error Handling Integration

### 4.1 Frontend Error Handling

```typescript
// src/hooks/useErrorHandler.ts
export const useErrorHandler = () => {
  const dispatch = useAppDispatch();

  const handleAPIError = useCallback((error: any) => {
    if (error.response?.data?.error) {
      const apiError = error.response.data.error;
      
      switch (apiError.code) {
        case 'TOKEN_EXPIRED':
          // Handle token expiry
          dispatch(refreshToken());
          break;
        case 'TRANSLATION_ERROR':
          // Handle translation errors
          dispatch(setTranslationError(apiError.message));
          break;
        case 'RATE_LIMIT_EXCEEDED':
          // Handle rate limiting
          const retryAfter = apiError.details?.retryAfter || 60;
          setTimeout(() => {
            // Retry the request
          }, retryAfter * 1000);
          break;
        default:
          // Generic error handling
          dispatch(setGlobalError(apiError.message));
      }
    } else {
      // Network or other errors
      dispatch(setGlobalError('An unexpected error occurred'));
    }
  }, [dispatch]);

  return { handleAPIError };
};
```

### 4.2 Backend Error Response Format

```python
# backend/src/core/exceptions.py
class APIException(Exception):
    def __init__(
        self, 
        code: str, 
        message: str, 
        status_code: int = 400, 
        details: dict = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "traceId": str(uuid.uuid4())
            }
        }
    )
```

---

## 5. Performance Optimization

### 5.1 Frontend Optimizations

```typescript
// src/hooks/useWebSocketOptimization.ts
export const useWebSocketOptimization = (websocketUrl: string) => {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const messageQueueRef = useRef<any[]>([]);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(websocketUrl);
    
    ws.onopen = () => {
      setIsConnected(true);
      
      // Send queued messages
      while (messageQueueRef.current.length > 0) {
        const message = messageQueueRef.current.shift();
        ws.send(JSON.stringify(message));
      }
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      
      // Implement exponential backoff for reconnection
      const reconnectDelay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
      reconnectTimeoutRef.current = setTimeout(connect, reconnectDelay);
      reconnectAttempts++;
    };

    wsRef.current = ws;
  }, [websocketUrl]);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      // Queue message for later sending
      messageQueueRef.current.push(message);
    }
  }, []);

  return { isConnected, sendMessage, connect };
};
```

### 5.2 Backend Performance Optimizations

```python
# backend/src/core/websocket_manager.py
class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.message_buffer: Dict[str, List[dict]] = {}
        self.processing_queue = asyncio.Queue()
        
    async def add_connection(self, session_id: str, websocket: WebSocket):
        self.connections[session_id] = websocket
        
        # Start background task for processing messages
        asyncio.create_task(self._process_messages(session_id))
    
    async def _process_messages(self, session_id: str):
        """Process messages in batches for better performance"""
        while session_id in self.connections:
            try:
                # Batch process messages every 50ms
                await asyncio.sleep(0.05)
                
                if session_id in self.message_buffer:
                    messages = self.message_buffer[session_id]
                    self.message_buffer[session_id] = []
                    
                    # Process messages in batch
                    await self._process_message_batch(session_id, messages)
                    
            except Exception as e:
                logger.error(f"Error processing messages for {session_id}: {e}")
    
    async def _process_message_batch(self, session_id: str, messages: List[dict]):
        """Process multiple messages together for efficiency"""
        audio_chunks = [msg for msg in messages if msg["type"] == "audio_chunk"]
        
        if audio_chunks:
            # Combine audio chunks for more efficient processing
            combined_audio = b"".join([
                base64.b64decode(chunk["data"]) for chunk in audio_chunks
            ])
            
            # Process combined audio
            result = await asr_service.transcribe_batch(combined_audio)
            
            # Send results back
            websocket = self.connections.get(session_id)
            if websocket:
                await websocket.send_text(json.dumps({
                    "type": "text_token",
                    "sessionId": session_id,
                    "text": result.text,
                    "confidence": result.confidence,
                    "timestamp": int(time.time() * 1000)
                }))
```

---

## 6. Testing Integration

### 6.1 Frontend Testing

```typescript
// src/components/translation/__tests__/TranslationInterface.test.tsx
describe('TranslationInterface', () => {
  let mockWebSocket: jest.Mocked<WebSocket>;
  
  beforeEach(() => {
    mockWebSocket = {
      send: jest.fn(),
      close: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
    } as any;
    
    global.WebSocket = jest.fn(() => mockWebSocket);
  });

  it('should establish WebSocket connection on mount', async () => {
    render(
      <TranslationInterface 
        mode="voice-to-isl" 
        sessionId="test-session" 
      />
    );
    
    await waitFor(() => {
      expect(global.WebSocket).toHaveBeenCalledWith(
        expect.stringContaining('ws://localhost:8000/ws/translation/test-session')
      );
    });
  });

  it('should send audio data via WebSocket', async () => {
    const { getByTestId } = render(
      <TranslationInterface mode="voice-to-isl" />
    );
    
    const recordButton = getByTestId('record-button');
    fireEvent.click(recordButton);
    
    // Simulate audio data
    const mockAudioData = new ArrayBuffer(1024);
    act(() => {
      // Trigger audio data event
    });
    
    await waitFor(() => {
      expect(mockWebSocket.send).toHaveBeenCalledWith(
        expect.stringContaining('"type":"audio_chunk"')
      );
    });
  });
});
```

### 6.2 Backend Testing

```python
# backend/tests/test_websocket.py
@pytest.mark.asyncio
async def test_translation_websocket():
    client = TestClient(app)
    
    with client.websocket_connect("/ws/translation/test-session?token=valid-token") as websocket:
        # Send audio chunk
        audio_message = {
            "type": "audio_chunk",
            "sessionId": "test-session",
            "data": base64.b64encode(b"fake-audio-data").decode(),
            "timestamp": int(time.time() * 1000)
        }
        
        websocket.send_text(json.dumps(audio_message))
        
        # Receive text token response
        response = websocket.receive_text()
        data = json.loads(response)
        
        assert data["type"] == "text_token"
        assert data["sessionId"] == "test-session"
        assert "text" in data
        assert "confidence" in data

@pytest.mark.asyncio
async def test_websocket_authentication():
    client = TestClient(app)
    
    # Test without token
    with pytest.raises(WebSocketException):
        with client.websocket_connect("/ws/translation/test-session"):
            pass
    
    # Test with invalid token
    with pytest.raises(WebSocketException):
        with client.websocket_connect("/ws/translation/test-session?token=invalid"):
            pass
```

---

## 7. Deployment Configuration

### 7.1 Frontend Environment Configuration

```typescript
// src/config/environment.ts
interface EnvironmentConfig {
  apiBaseUrl: string;
  wsBaseUrl: string;
  enableLogging: boolean;
  maxRetries: number;
  requestTimeout: number;
}

const development: EnvironmentConfig = {
  apiBaseUrl: 'http://localhost:8000',
  wsBaseUrl: 'ws://localhost:8000',
  enableLogging: true,
  maxRetries: 3,
  requestTimeout: 10000,
};

const production: EnvironmentConfig = {
  apiBaseUrl: 'https://api.isl-translator.com',
  wsBaseUrl: 'wss://api.isl-translator.com',
  enableLogging: false,
  maxRetries: 5,
  requestTimeout: 15000,
};

export const config = process.env.NODE_ENV === 'production' ? production : development;
```

### 7.2 Backend Configuration

```python
# backend/src/config/settings.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "h2:file:./data/isl_translator.db"
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 30
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # WebSocket
    websocket_heartbeat_interval: int = 30
    websocket_max_connections: int = 1000
    
    # Translation Services
    asr_service_url: str = "http://localhost:8001"
    nlp_service_url: str = "http://localhost:8002"
    animation_service_url: str = "http://localhost:8003"
    tts_service_url: str = "http://localhost:8004"
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

*This Frontend-Backend Integration Mapping document provides comprehensive guidance for integrating the React frontend with the FastAPI backend for the Real-time Bidirectional Voice-to-ISL & ISL-to-Voice Translation System. It covers all major components, API interactions, state management, error handling, performance optimization, testing, and deployment considerations.*
