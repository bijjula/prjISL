# Voice-to-ISL Translation System (MVS)

Real-time Bidirectional Voice-to-ISL & ISL-to-Voice Translation System - Minimum Viable Scope Implementation

## 📋 Overview

This is a complete, self-contained **Minimum Viable Scope (MVS)** implementation demonstrating the core Voice-to-ISL translation workflow. The system consists of a **FastAPI backend** simulating L4 Core Data Plane services and a **React TypeScript frontend** with a responsive four-quadrant user interface.

### 🎯 System Architecture

| Layer | Component | Technology | Purpose |
|-------|-----------|------------|---------|
| **L1 - Client Layer** | React Frontend | TypeScript + CSS | User interface with four-quadrant layout |
| **L2 - API Gateway** | FastAPI Backend | Python + Pydantic | API orchestration and service coordination |
| **L4 - Core Services** | Mock Services | Python Functions | ASR, NLP Translation, Animation Engine simulation |

### 🔄 Translation Workflow

```
Voice Input → ASR Service → NLP Translator → Animation Engine → ISL Avatar
     ↓              ↓              ↓               ↓
Text Input    Text Tokens    ISL Gloss    Avatar Stream URL
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** with pip
- **Node.js 16+** with npm
- **Modern web browser** (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)

### ⚡ One-Command Setup & Run

Choose your operating system:

#### 🐧 macOS / Linux
```bash
# One-time setup (run this first)
./setup.sh

# Start the application
./start.sh

# Stop the application
./stop.sh
```

#### 🪟 Windows
```cmd
# One-time setup (run this first in Command Prompt)
setup.bat

# Start the application
start.bat

# Stop the application
stop.bat
```

> **Note**: Windows users can also use the `.sh` scripts in Git Bash or WSL.

### 🔧 What the Scripts Do

The setup and start scripts automatically:

1. ✅ **Check Prerequisites**: Verify Python 3.9+ and Node.js 16+ are installed
2. ✅ **Setup Backend**: Create virtual environment, install FastAPI dependencies
3. ✅ **Setup Frontend**: Install React/TypeScript dependencies
4. ✅ **Start Services**: Launch backend (port 8000) and frontend (port 3000)
5. ✅ **Open Browser**: Automatically open http://localhost:3000
6. ✅ **Handle Cleanup**: Stop existing processes, free up ports

### Script Options

```bash
# Start with options
./start.sh --help           # Show help
./start.sh --clean          # Clean install (removes node_modules, venv)
./start.sh --no-browser     # Don't open browser automatically

# Example: Clean install without opening browser
./start.sh --clean --no-browser
```

### 🌐 Access Points

Once running, access the application at:

- **Frontend App**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/api/docs  
- **Health Check**: http://localhost:8000/health
- **API Endpoint**: http://localhost:8000/api/v1/translate/voice-to-isl

### 🆘 Manual Setup (If Scripts Fail)

<details>
<summary>Click to expand manual setup instructions</summary>

#### Backend Setup
```bash
cd backend/
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend/
npm install
npm start
```

</details>

## 📁 Project Structure

```
prjISL/
├── backend/
│   ├── main.py                 # FastAPI application with translation endpoint
│   ├── schemas.py              # Pydantic models for request/response validation
│   └── requirements.txt        # Python dependencies (create this)
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── VoiceToISL.tsx     # Main React component
│   │   ├── VoiceToISL.css     # Responsive styles
│   │   ├── App.tsx            # App root component
│   │   └── index.tsx          # React entry point
│   ├── package.json           # Node.js dependencies
│   └── tsconfig.json          # TypeScript configuration
├── document/                  # Project documentation
├── README.md                  # This file
└── .gitignore                # Git ignore rules
```

## 🔌 API Reference

### Core Translation Endpoint

**POST** `/api/v1/translate/voice-to-isl`

Translates voice input (simulated as text) to ISL gloss notation and avatar stream.

#### Request Body
```json
{
  "audio_text": "Hello, how are you?"
}
```

#### Response (200 OK)
```json
{
  "source_text": "Hello, how are you?",
  "isl_gloss": "HELLO HOW YOU?",
  "avatar_stream_url": "ws://localhost:8000/avatar/stream/avatar_pose_stream_a1b2c3d4_1635123456",
  "confidence": 0.92,
  "processing_time_ms": 234.56
}
```

#### Error Response (400 Bad Request)
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input validation failed: audio_text cannot be empty",
    "timestamp": "2024-10-25T10:30:00.000Z"
  }
}
```

### Health Check Endpoint

**GET** `/health`

Returns system health and operational metrics.

#### Response
```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "service_status": "operational",
  "translations_processed": 142,
  "timestamp": "2024-10-25T10:30:00.000Z"
}
```

## 🎨 Four-Quadrant User Interface

The frontend implements a responsive four-quadrant layout:

| Quadrant | Location | Purpose | Data Source |
|----------|----------|---------|-------------|
| **Voice Recording** | Top-Left | Simulated voice input capture | User input simulation |
| **Text Tokens** | Bottom-Left | Transcribed text display | ASR Service output (`source_text`) |
| **ISL Gloss** | Top-Right | ISL gloss notation | NLP Translator output (`isl_gloss`) |
| **Avatar Rendering** | Bottom-Right | 3D avatar animation placeholder | Animation Engine output (`avatar_stream_url`) |

### 📱 Responsive Design Features

- **Mobile-First**: Optimized for mobile devices with stacked quadrants
- **Tablet Layout**: 2x2 grid on medium screens (768px+)
- **Desktop Layout**: Enhanced 2x2 grid with hover effects
- **Accessibility**: WCAG 2.1 compliance with keyboard navigation
- **High Contrast**: Support for high contrast mode
- **Reduced Motion**: Respects user motion preferences

## 🧪 Testing the Application

### Manual Testing Steps

1. **Start both backend and frontend servers**
2. **Open the application** in your web browser
3. **Check API connectivity** - Green status indicator should show "✅ API Connected"
4. **Test translation workflow**:

   **Sample Input**: "Hello, how are you?"
   **Expected Output**:
   - **Text Tokens**: "Hello, how are you?"
   - **ISL Gloss**: "HELLO HOW YOU?"
   - **Avatar Stream**: Generated stream URL
   - **Processing Time**: ~200-300ms

5. **Try sample texts** using the quick sample buttons
6. **Test error handling** by submitting empty input
7. **Test responsive design** by resizing browser window

### Sample Test Cases

| Input Text | Expected ISL Gloss | Notes |
|------------|-------------------|-------|
| "Hello, how are you?" | "HELLO HOW YOU?" | Basic greeting |
| "Good morning" | "MORNING GOOD" | Word order adjustment |
| "Thank you for your help" | "THANK-YOU YOUR HELP" | Complex phrase |
| "Where is the hospital?" | "WHERE HOSPITAL?" | Question format |
| "My name is John" | "MY NAME JOHN" | Identity introduction |

### Error Testing

| Test Case | Input | Expected Behavior |
|-----------|-------|-------------------|
| Empty input | `""` | Error message: "Please enter some text to translate" |
| Backend offline | Any text | Red status indicator + connection error |
| Very long text | 1000+ characters | Character limit warning |

## 🛠️ Development Guidelines

### Backend Development (Python)

- **Code Style**: PEP 8 compliance with snake_case naming
- **Type Hints**: All functions must include proper type annotations
- **Error Handling**: Use FastAPI's HTTPException for API errors
- **Logging**: Structured logging with appropriate log levels
- **Documentation**: Comprehensive docstrings for all functions

### Frontend Development (TypeScript/React)

- **Code Style**: ESLint + Prettier configuration
- **Naming**: camelCase for variables/functions, PascalCase for components
- **Components**: Functional components with TypeScript interfaces
- **State Management**: React hooks (useState, useEffect)
- **Error Handling**: try-catch blocks with user-friendly error messages

### CSS Standards

- **Methodology**: Mobile-first responsive design
- **Units**: Relative units (rem, em, %) preferred over fixed pixels
- **Layout**: Flexbox and CSS Grid for responsive layouts
- **Accessibility**: High contrast and reduced motion support
- **Variables**: CSS custom properties for consistent theming

## 🔧 Configuration

### Backend Configuration

Environment variables (create `.env` file if needed):

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Mock Service Settings
ASR_PROCESSING_DELAY=0.05
NLP_PROCESSING_DELAY=0.1
ANIMATION_PROCESSING_DELAY=0.08
```

### Frontend Configuration

Update API base URL if backend runs on different port:

```typescript
// In VoiceToISL.tsx
const API_BASE_URL = 'http://localhost:8000';
```

## 📊 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **End-to-End Latency** | <1000ms | Full translation pipeline |
| **API Response Time** | <200ms | Individual service calls |
| **Frontend Load Time** | <2s | Initial page load |
| **Translation Accuracy** | >85% | Mock gloss conversion quality |
| **UI Responsiveness** | 60fps | Smooth animations and transitions |

## 🚀 Deployment

### Local Development Deployment

1. **Backend**: `uvicorn main:app --reload --port 8000`
2. **Frontend**: `npm start` or `npm run dev`

### Production Considerations

For production deployment (beyond MVS scope):

- **Backend**: Use production ASGI server (Gunicorn + Uvicorn)
- **Frontend**: Build and serve static files (`npm run build`)
- **Database**: Replace mock data with persistent storage
- **Security**: Add authentication, rate limiting, HTTPS
- **Monitoring**: Implement proper logging and metrics collection
- **Containerization**: Docker containers for scalable deployment

## 🔍 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.9+

# Check if port 8000 is available
lsof -i :8000

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

#### Frontend Won't Start
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 16+
```

#### CORS Errors
- Verify backend CORS configuration includes frontend URL
- Check that both servers are running on expected ports
- Clear browser cache and cookies

#### API Connection Issues
- Verify backend health endpoint: http://localhost:8000/health
- Check browser developer console for network errors
- Ensure firewall isn't blocking local connections

### Debug Mode

Enable debug logging in backend:

```python
# In main.py
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Technical Documentation

### Architecture Documents
- [Product Requirement Document](document/Product_Requirement_Document.md)
- [Functional Specification](document/Functional_Specification_Document.md)
- [API Specifications](document/API_Specifications.md)

### Mock Service Implementation

The MVS implementation uses mock services to simulate real AI/ML components:

1. **ASR Service** (`mock_asr_service`): Pass-through text processing
2. **NLP Translator** (`text_to_isl_gloss`): Rule-based text-to-gloss conversion
3. **Animation Engine** (`gloss_to_avatar_stream`): Stream URL generation

### Future Enhancements

Beyond MVS scope:
- Real ASR model integration (Whisper, Google Speech-to-Text)
- Computer vision for ISL gesture recognition
- Advanced NLP models for accurate translation
- 3D avatar animation with Three.js
- WebRTC for real-time audio/video streaming
- Database integration for user sessions
- Authentication and user management

## 🤝 Contributing

This is an MVS implementation for demonstration purposes. For the full production system:

1. Follow the coding standards outlined in this README
2. All code changes require proper testing
3. Update documentation for new features
4. Follow the established git workflow

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For technical issues or questions about this MVS implementation:

- **Documentation**: Check the `document/` directory for detailed specifications
- **API Issues**: Test endpoints using the Swagger UI at http://localhost:8000/api/docs
- **Frontend Issues**: Check browser developer console for errors
- **Performance**: Monitor network tab for API response times

---

**🎉 Success Criteria**: You have successfully implemented the Voice-to-ISL Translation MVS when:
- ✅ Backend API responds to translation requests with proper ISL gloss
- ✅ Frontend displays all four quadrants with correct data flow
- ✅ Responsive design works on mobile, tablet, and desktop
- ✅ Error handling provides clear user feedback
- ✅ Sample translations demonstrate the core workflow

**Happy Coding! 🚀**
