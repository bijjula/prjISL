# API Specifications Document
## Real-time Bidirectional Voice-to-ISL & ISL-to-Voice Translation System

| Document Information | Details |
|---------------------|---------|
| **API Version** | v1.0 |
| **Document Date** | October 25, 2024 |
| **Base URL** | `https://api.isl-translator.com` |
| **Authentication** | JWT Bearer Token |
| **Content Type** | `application/json` |

---

## 1. Authentication APIs

### 1.1 User Registration

**Endpoint:** `POST /api/v1/auth/register`

**Description:** Register a new user account

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "string (3-50 chars, alphanumeric + underscore)",
  "email": "string (valid email format)",
  "password": "string (min 8 chars, 1 uppercase, 1 lowercase, 1 number)",
  "userType": "hearing | deaf | admin",
  "firstName": "string (1-50 chars)",
  "lastName": "string (1-50 chars)",
  "preferredLanguage": "string (en, hi, ta, te, bn, etc.)",
  "avatarSettings": {
    "skin": "string",
    "clothing": "string",
    "accessories": "array"
  }
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "userId": "uuid",
    "accessToken": "string (JWT)",
    "refreshToken": "string",
    "expiresIn": 3600,
    "userProfile": {
      "userId": "uuid",
      "username": "string",
      "email": "string",
      "userType": "string",
      "firstName": "string",
      "lastName": "string",
      "preferredLanguage": "string",
      "avatarSettings": "object",
      "createdAt": "datetime",
      "isActive": true
    }
  }
}
```

**Error Responses:**
```json
// 400 Bad Request - Validation Error
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "message": "Invalid email format"
    },
    "timestamp": "2024-10-25T10:30:00Z",
    "traceId": "uuid"
  }
}

// 409 Conflict - User Exists
{
  "error": {
    "code": "USER_EXISTS",
    "message": "Username or email already registered",
    "timestamp": "2024-10-25T10:30:00Z",
    "traceId": "uuid"
  }
}
```

### 1.2 User Login

**Endpoint:** `POST /api/v1/auth/login`

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "accessToken": "string (JWT)",
    "refreshToken": "string",
    "expiresIn": 3600,
    "userProfile": {
      "userId": "uuid",
      "username": "string",
      "email": "string",
      "userType": "string",
      "firstName": "string", 
      "lastName": "string",
      "preferredLanguage": "string",
      "lastLoginAt": "datetime"
    }
  }
}
```

### 1.3 Token Refresh

**Endpoint:** `POST /api/v1/auth/refresh`

**Request Body:**
```json
{
  "refreshToken": "string"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "accessToken": "string (JWT)",
    "refreshToken": "string",
    "expiresIn": 3600
  }
}
```

### 1.4 User Logout

**Endpoint:** `POST /api/v1/auth/logout`

**Request Headers:**
```
Authorization: Bearer {accessToken}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Successfully logged out"
}
```

---

## 2. User Profile APIs

### 2.1 Get User Profile

**Endpoint:** `GET /api/v1/auth/profile`

**Request Headers:**
```
Authorization: Bearer {accessToken}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "userId": "uuid",
    "username": "string",
    "email": "string",
    "userType": "string",
    "firstName": "string",
    "lastName": "string",
    "preferredLanguage": "string",
    "avatarSettings": {
      "skin": "string",
      "clothing": "string", 
      "accessories": "array"
    },
    "createdAt": "datetime",
    "lastLoginAt": "datetime",
    "isActive": true
  }
}
```

### 2.2 Update User Profile

**Endpoint:** `PUT /api/v1/auth/profile`

**Request Headers:**
```
Authorization: Bearer {accessToken}
Content-Type: application/json
```

**Request Body:**
```json
{
  "firstName": "string (optional)",
  "lastName": "string (optional)",
  "preferredLanguage": "string (optional)",
  "avatarSettings": {
    "skin": "string (optional)",
    "clothing": "string (optional)",
    "accessories": "array (optional)"
  }
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "userId": "uuid",
    "username": "string",
    "email": "string",
    "userType": "string",
    "firstName": "string",
    "lastName": "string",
    "preferredLanguage": "string",
    "avatarSettings": "object",
    "updatedAt": "datetime"
  }
}
```

---

## 3. Friend Management APIs

### 3.1 Search Users

**Endpoint:** `GET /api/v1/friends/search`

**Request Headers:**
```
Authorization: Bearer {accessToken}
```

**Query Parameters:**
```
q: string (username or email to search)
limit: number (default: 20, max: 100)
offset: number (default: 0)
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "userId": "uuid",
        "username": "string",
        "firstName": "string",
        "lastName": "string",
        "userType": "string",
        "avatarSettings": "object",
        "friendshipStatus": "none | pending_sent | pending_received | friends"
      }
    ],
    "pagination": {
      "total": 50,
      "limit": 20,
      "offset": 0,
      "hasMore": true
    }
  }
}
```

### 3.2 Send Friend Request

**Endpoint:** `POST /api/v1/friends/request`

**Request Headers:**
```
Authorization: Bearer {accessToken}
Content-Type: application/json
```

**Request Body:**
```json
{
  "userId": "uuid",
  "message": "string (optional, max 200 chars)"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "friendshipId": "uuid",
    "requesterId": "uuid",
    "addresseeId": "uuid",
    "status": "pending",
    "message": "string",
    "createdAt": "datetime"
  }
}
```

### 3.3 Get Friend Requests

**Endpoint:** `GET /api/v1/friends/requests`

**Request Headers:**
```
Authorization: Bearer {accessToken}
```

**Query Parameters:**
```
type: string (sent | received | all, default: received)
status: string (pending | accepted | declined, default: pending)
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "requests": [
      {
        "friendshipId": "uuid",
        "requester": {
          "userId": "uuid",
          "username": "string",
          "firstName": "string",
          "lastName": "string",
          "avatarSettings": "object"
        },
        "addressee": {
          "userId": "uuid",
          "username": "string", 
          "firstName": "string",
          "lastName": "string",
          "avatarSettings": "object"
        },
        "status": "string",
        "message": "string",
        "createdAt": "datetime"
      }
    ]
  }
}
```

### 3.4 Accept Friend Request

**Endpoint:** `PUT /api/v1/friends/accept/{friendshipId}`

**Request Headers:**
```
Authorization: Bearer {accessToken}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "friendshipId": "uuid",
    "status": "accepted",
    "updatedAt": "datetime"
  }
}
```

### 3.5 Decline Friend Request

**Endpoint:** `DELETE /api/v1/friends/decline/{friendshipId}`

**Request Headers:**
```
Authorization: Bearer {accessToken}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Friend request declined"
}
```

### 3.6 Get Friends List

**Endpoint:** `GET /api/v1/friends/list`

**Request Headers:**
```
Authorization: Bearer {accessToken}
```

**Query Parameters:**
```
status: string (online | offline | all, default: all)
limit: number (default: 50, max: 200)
offset: number (default: 0)
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "friends": [
      {
        "userId": "uuid",
        "username": "string",
        "firstName": "string",
        "lastName": "string",
        "userType": "string",
        "avatarSettings": "object",
        "isOnline": true,
        "lastSeen": "datetime",
        "friendsSince": "datetime"
      }
    ],
    "pagination": {
      "total": 25,
      "limit": 50,
      "offset": 0
    }
  }
}
```

### 3.7 Remove Friend

**Endpoint:** `DELETE /api/v1/friends/remove/{userId}`

**Request Headers:**
```
Authorization: Bearer {accessToken}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Friend removed successfully"
}
```

---

## 4. Translation APIs

### 4.1 Voice to ISL Translation

**Endpoint:** `POST /api/v1/translate/voice-to-isl`

**Request Headers:**
```
Authorization: Bearer {accessToken}
Content-Type: application/json
```

**Request Body:**
```json
{
  "audioData": "string (base64 encoded audio)",
  "format": "string (webm, ogg, wav, mp3)",
  "sampleRate": "number (16000, 44100, 48000)",
  "channels": "number (1 or 2)",
  "language": "string (hi, en, ta, te, bn)",
  "sessionId": "uuid (optional)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "sessionId": "uuid",
    "sourceText": "string (transcribed text)",
    "islGloss": "string (ISL gloss notation)",
    "avatarStreamUrl": "string (URL to avatar animation stream)",
    "confidence": {
      "asr": 0.95,
      "translation": 0.88,
      "overall": 0.91
    },
    "processingTime": 850,
    "timestamp": "datetime"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": {
    "code": "INVALID_AUDIO_FORMAT",
    "message": "Unsupported audio format or corrupted data",
    "details": {
      "supportedFormats": ["webm", "ogg", "wav", "mp3"],
      "maxDuration": 300
    },
    "timestamp": "2024-10-25T10:30:00Z",
    "traceId": "uuid"
  }
}
```

### 4.2 ISL to Voice Translation

**Endpoint:** `POST /api/v1/translate/isl-to-voice`

**Request Headers:**
```
Authorization: Bearer {accessToken}
Content-Type: application/json
```

**Request Body:**
```json
{
  "videoData": "string (base64 encoded video)",
  "poseData": {
    "landmarks": "array (optional - pre-extracted pose landmarks)",
    "timestamp": "number"
  },
  "format": "string (webm, mp4)",
  "frameRate": "number (15-30)",
  "language": "string (hi, en, ta, te, bn)",
  "sessionId": "uuid (optional)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "sessionId": "uuid",
    "sourceGloss": "string (recognized ISL gloss)",
    "transcribedText": "string (converted text)",
    "audioStreamUrl": "string (URL to synthesized speech)",
    "confidence": {
      "slr": 0.89,
      "translation": 0.92,
      "tts": 0.96,
      "overall": 0.92
    },
    "processingTime": 920,
    "timestamp": "datetime"
  }
}
```

### 4.3 Start Streaming Translation

**Endpoint:** `POST /api/v1/translate/stream/start`

**Request Headers:**
```
Authorization: Bearer {accessToken}
Content-Type: application/json
```

**Request Body:**
```json
{
  "mode": "voice-to-isl | isl-to-voice | bidirectional",
  "language": "string (hi, en, ta, te, bn)",
  "quality": "low | medium | high",
  "participantId": "uuid (optional - for conversation mode)"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "sessionId": "uuid",
    "websocketUrl": "wss://api.isl-translator.com/ws/translation/{sessionId}",
    "mode": "string",
    "language": "string",
    "quality": "string",
    "createdAt": "datetime",
    "expiresAt": "datetime"
  }
}
```

### 4.4 End Streaming Translation

**Endpoint:** `POST /api/v1/translate/stream/end`

**Request Headers:**
```
Authorization: Bearer {accessToken}
Content-Type: application/json
```

**Request Body:**
```json
{
  "sessionId": "uuid"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "sessionId": "uuid",
    "duration": 1250,
    "totalMessages": 45,
    "averageLatency": 890,
    "endedAt": "datetime"
  }
}
```

---

## 5. Conversation APIs

### 5.1 Start Conversation

**Endpoint:** `POST /api/v1/conversations/start`

**Request Headers:**
```
Authorization: Bearer {accessToken}
Content-Type: application/json
```

**Request Body:**
```json
{
  "participantIds": ["uuid"],
  "translationMode": "voice-to-isl | isl-to-voice | bidirectional",
  "language": "string (hi, en, ta, te, bn)",
  "recordConversation": "boolean (default: false)"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "conversationId": "uuid",
    "participants": [
      {
        "userId": "uuid",
        "username": "string",
        "userType": "string",
        "joinedAt": "datetime"
      }
    ],
    "translationMode": "string",
    "language": "string",
    "recordConversation": "boolean",
    "websocketUrl": "wss://api.isl-translator.com/ws/conversation/{conversationId}",
    "startTime": "datetime",
    "status": "active"
  }
}
```

### 5.2 Join Conversation

**Endpoint:** `POST /api/v1/conversations/{conversationId}/join`

**Request Headers:**
```
Authorization: Bearer {accessToken}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "conversationId": "uuid",
    "participants": [
      {
        "userId": "uuid",
        "username": "string",
        "userType": "string",
        "joinedAt": "datetime"
      }
    ],
    "websocketUrl": "wss://api.isl-translator.com/ws/conversation/{conversationId}",
    "joinedAt": "datetime"
  }
}
```

### 5.3 Leave Conversation

**Endpoint:** `POST /api/v1/conversations/{conversationId}/leave`

**Request Headers:**
```
Authorization: Bearer {accessToken}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Left conversation successfully",
  "leftAt": "datetime"
}
```

### 5.4 End Conversation

**Endpoint:** `PUT /api/v1/conversations/{conversationId}/end`

**Request Headers:**
```
Authorization: Bearer {accessToken}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "conversationId": "uuid",
    "duration": 1850,
    "totalMessages": 78,
    "endTime": "datetime",
    "status": "ended"
  }
}
```

### 5.5 Get Active Conversations

**Endpoint:** `GET /api/v1/conversations/active`

**Request Headers:**
```
Authorization: Bearer {accessToken}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "conversations": [
      {
        "conversationId": "uuid",
        "participants": [
          {
            "userId": "uuid",
            "username": "string",
            "userType": "string"
          }
        ],
        "translationMode": "string",
        "startTime": "datetime",
        "status": "active"
      }
    ]
  }
}
```

### 5.6 Get Conversation History

**Endpoint:** `GET /api/v1/conversations/history`

**Request Headers:**
```
Authorization: Bearer {accessToken}
```

**Query Parameters:**
```
limit: number (default: 20, max: 100)
offset: number (default: 0)
startDate: string (ISO date, optional)
endDate: string (ISO date, optional)
participantId: uuid (optional)
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "conversations": [
      {
        "conversationId": "uuid",
        "participants": [
          {
            "userId": "uuid",
            "username": "string",
            "userType": "string"
          }
        ],
        "translationMode": "string",
        "startTime": "datetime",
        "endTime": "datetime",
        "duration": 1850,
        "totalMessages": 78,
        "status": "ended"
      }
    ],
    "pagination": {
      "total": 150,
      "limit": 20,
      "offset": 0,
      "hasMore": true
    }
  }
}
```

---

## 6. WebSocket APIs

### 6.1 Translation WebSocket

**Connection URL:** `wss://api.isl-translator.com/ws/translation/{sessionId}`

**Authentication:** Include JWT token as query parameter: `?token={accessToken}`

#### Incoming Message Types (Client → Server)

**Audio Chunk:**
```json
{
  "type": "audio_chunk",
  "sessionId": "uuid",
  "data": "string (base64 audio data)",
  "sequence": 1,
  "timestamp": 1698234567890,
  "format": "string",
  "sampleRate": 16000
}
```

**Video Frame:**
```json
{
  "type": "video_frame", 
  "sessionId": "uuid",
  "data": "string (base64 video data)",
  "sequence": 1,
  "timestamp": 1698234567890,
  "format": "string",
  "frameRate": 30
}
```

**Pose Data:**
```json
{
  "type": "pose_data",
  "sessionId": "uuid",
  "poses": {
    "face": "array (facial landmarks)",
    "leftHand": "array (hand landmarks)",
    "rightHand": "array (hand landmarks)",
    "body": "array (body pose landmarks)"
  },
  "timestamp": 1698234567890
}
```

#### Outgoing Message Types (Server → Client)

**Text Token:**
```json
{
  "type": "text_token",
  "sessionId": "uuid",
  "text": "Hello",
  "confidence": 0.95,
  "isFinal": false,
  "timestamp": 1698234567890
}
```

**ISL Gloss:**
```json
{
  "type": "isl_gloss",
  "sessionId": "uuid", 
  "gloss": "HELLO",
  "confidence": 0.88,
  "timestamp": 1698234567890
}
```

**Avatar Pose:**
```json
{
  "type": "avatar_pose",
  "sessionId": "uuid",
  "poseData": {
    "rotation": [0, 0, 0],
    "position": [0, 0, 0],
    "joints": {
      "leftShoulder": [0.1, 0.2, 0.3],
      "rightShoulder": [0.1, 0.2, 0.3]
    }
  },
  "timestamp": 1698234567890
}
```

**Audio Chunk:**
```json
{
  "type": "audio_chunk",
  "sessionId": "uuid",
  "data": "string (base64 audio data)",
  "timestamp": 1698234567890
}
```

**Error Message:**
```json
{
  "type": "error",
  "sessionId": "uuid",
  "error": {
    "code": "TRANSLATION_ERROR",
    "message": "Translation service temporarily unavailable",
    "canRetry": true
  },
  "timestamp": 1698234567890
}
```

### 6.2 Conversation WebSocket

**Connection URL:** `wss://api.isl-translator.com/ws/conversation/{conversationId}`

**Authentication:** Include JWT token as query parameter: `?token={accessToken}`

#### Message Types

**Participant Joined:**
```json
{
  "type": "participant_joined",
  "conversationId": "uuid",
  "participant": {
    "userId": "uuid",
    "username": "string",
    "userType": "string"
  },
  "timestamp": 1698234567890
}
```

**Participant Left:**
```json
{
  "type": "participant_left",
  "conversationId": "uuid",
  "participant": {
    "userId": "uuid",
    "username": "string"
  },
  "timestamp": 1698234567890
}
```

**Conversation Ended:**
```json
{
  "type": "conversation_ended",
  "conversationId": "uuid",
  "endedBy": "uuid",
  "duration": 1850,
  "timestamp": 1698234567890
}
```

---

## 7. Admin APIs

### 7.1 Get All Users

**Endpoint:** `GET /api/v1/admin/users`

**Request Headers:**
```
Authorization: Bearer {adminAccessToken}
```

**Query Parameters:**
```
limit: number (default: 50, max: 200)
offset: number (default: 0)
userType: string (hearing | deaf | admin, optional)
status: string (active | inactive, optional)
search: string (search by username or email, optional)
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "userId": "uuid",
        "username": "string",
        "email": "string",
        "userType": "string",
        "firstName": "string",
        "lastName": "string",
        "isActive": true,
        "createdAt": "datetime",
        "lastLoginAt": "datetime",
        "totalSessions": 25,
        "totalFriends": 10
      }
    ],
    "pagination": {
      "total": 500,
      "limit": 50,
      "offset": 0,
      "hasMore": true
    }
  }
}
```

### 7.2 Get User Details

**Endpoint:** `GET /api/v1/admin/users/{userId}`

**Request Headers:**
```
Authorization: Bearer {adminAccessToken}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "userId": "uuid",
    "username": "string",
    "email": "string",
    "userType": "string",
    "firstName": "string",
    "lastName": "string",
    "preferredLanguage": "string",
    "isActive": true,
    "createdAt": "datetime",
    "lastLoginAt": "datetime",
    "statistics": {
      "totalSessions": 125,
      "totalTranslations": 2450,
      "totalFriends": 15,
      "averageSessionDuration": 850,
      "lastActiveDate": "datetime"
    }
  }
}
```

### 7.3 Deactivate User

**Endpoint:** `PUT /api/v1/admin/users/{userId}/deactivate`

**Request Headers:**
```
Authorization: Bearer {adminAccessToken}
Content-Type: application/json
```

**Request Body:**
```json
{
  "reason": "string (optional)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "User deactivated successfully",
  "deactivatedAt": "datetime"
}
```

### 7.4 System Statistics

**Endpoint:** `GET /api/v1/admin/statistics`

**Request Headers:**
```
Authorization: Bearer {adminAccessToken}
```

**Query Parameters:**
```
startDate: string (ISO date, optional)
endDate: string (ISO date, optional)
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "users": {
      "total": 10000,
      "active": 8500,
      "deaf": 4000,
      "hearing": 5800,
      "admin": 200,
      "newThisMonth": 1200
    },
    "translations": {
      "totalToday": 5000,
      "totalThisMonth": 150000,
      "averageLatency": 890,
      "successRate": 0.987
    },
    "conversations": {
      "activeNow": 250,
      "totalToday": 1200,
      "totalThisMonth": 35000,
      "averageDuration": 1450
    },
    "system": {
      "uptime": 0.999,
      "errorRate": 0.001,
      "responseTime": 185,
      "lastDeployment": "datetime"
    }
  }
}
```

---

## 8. Health Check & System APIs

### 8.1 Health Check

**Endpoint:** `GET /api/v1/health`

**Description:** Basic health check endpoint

**Success Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-10-25T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "messageQueue": "healthy"
  }
}
```

### 8.2 System Status

**Endpoint:** `GET /api/v1/status`

**Success Response (200 OK):**
```json
{
  "status": "operational",
  "timestamp": "2024-10-25T10:30:00Z",
  "services": {
    "asrService": {
      "status": "healthy",
      "responseTime": 150,
      "lastCheck": "2024-10-25T10:29:00Z"
    },
    "slrService": {
      "status": "healthy", 
      "responseTime": 200,
      "lastCheck": "2024-10-25T10:29:00Z"
    },
    "nlpService": {
      "status": "healthy",
      "responseTime": 120,
      "lastCheck": "2024-10-25T10:29:00Z"
    },
    "animationService": {
      "status": "healthy",
      "responseTime": 80,
      "lastCheck": "2024-10-25T10:29:00Z"
    },
    "ttsService": {
      "status": "healthy",
      "responseTime": 180,
      "lastCheck": "2024-10-25T10:29:00Z"
    }
  },
  "metrics": {
    "activeUsers": 1250,
    "activeSessions": 340,
    "translationsPerMinute": 450
  }
}
```

---

## 9. Error Codes Reference

### 9.1 HTTP Status Codes

| Status Code | Description | Usage |
|-------------|-------------|--------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST (resource created) |
| 400 | Bad Request | Invalid request data or parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Resource already exists or conflict |
| 422 | Unprocessable Entity | Valid syntax but semantic errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Service temporarily down |

### 9.2 Application Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `INVALID_CREDENTIALS` | 401 | Wrong email/password combination |
| `TOKEN_EXPIRED` | 401 | JWT token has expired |
| `TOKEN_INVALID` | 401 | JWT token is malformed or invalid |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required permissions |
| `USER_NOT_FOUND` | 404 | User does not exist |
| `CONVERSATION_NOT_FOUND` | 404 | Conversation does not exist |
| `SESSION_NOT_FOUND` | 404 | Translation session does not exist |
| `USER_EXISTS` | 409 | Username or email already taken |
| `FRIEND_REQUEST_EXISTS` | 409 | Friend request already sent |
| `ALREADY_FRIENDS` | 409 | Users are already friends |
| `INVALID_AUDIO_FORMAT` | 400 | Unsupported audio format |
| `INVALID_VIDEO_FORMAT` | 400 | Unsupported video format |
| `FILE_TOO_LARGE` | 400 | File exceeds size limit |
| `TRANSLATION_ERROR` | 500 | Translation service error |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily down |

---

## 10. Rate Limiting

### 10.1 Rate Limit Rules

| Endpoint Category | Limit | Window | Headers |
|------------------|--------|--------|---------|
| Authentication | 10 requests | 1 minute | X-RateLimit-* |
| Translation | 100 requests | 1 minute | X-RateLimit-* |
| Friend Management | 50 requests | 1 minute | X-RateLimit-* |
| Profile Updates | 20 requests | 1 minute | X-RateLimit-* |
| Admin APIs | 200 requests | 1 minute | X-RateLimit-* |

### 10.2 Rate Limit Headers

All API responses include rate limiting information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1698234567
X-RateLimit-Window: 60
```

### 10.3 Rate Limit Exceeded Response

**Status Code:** 429 Too Many Requests

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 30 seconds.",
    "details": {
      "limit": 100,
      "window": 60,
      "retryAfter": 30
    },
    "timestamp": "2024-10-25T10:30:00Z",
    "traceId": "uuid"
  }
}
```

---

## 11. Pagination

### 11.1 Request Parameters

```
limit: number (items per page, default varies by endpoint)
offset: number (items to skip, default: 0)
```

### 11.2 Response Format

```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "total": 500,
      "limit": 20,
      "offset": 0,
      "hasMore": true,
      "nextOffset": 20,
      "prevOffset": null
    }
  }
}
```

---

## 12. API Versioning

### 12.1 Versioning Strategy

- **URL-based versioning**: `/api/v1/`, `/api/v2/`
- **Backward compatibility**: Maintained for at least 2 major versions
- **Deprecation notice**: 6 months advance notice via response headers
- **Migration guide**: Provided for breaking changes

### 12.2 Deprecation Headers

```
X-API-Deprecation-Date: 2024-12-01
X-API-Deprecation-Info: https://docs.isl-translator.com/migration/v2
X-API-Sunset-Date: 2025-06-01
```

---

*This API specification document serves as the comprehensive reference for integrating with the Real-time Bidirectional Voice-to-ISL & ISL-to-Voice Translation System APIs. For additional support, contact the development team or refer to the SDK documentation.*
