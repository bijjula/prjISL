## 👑 The Directive: Core Task

Write a complete, self-contained **Minimum Viable Scope (MVS)** Python application using **FastAPI** for the backend API and **React (TypeScript)** for the frontend page to demonstrate the core **Voice-to-ISL** translation workflow.

The output must consist of four files:

1.  **`backend/main.py`**: The FastAPI application with the required endpoint.
2.  **`backend/schemas.py`**: Pydantic schemas for request/response validation.
3.  **`frontend/src/VoiceToISL.tsx`**: The main React functional component for the user interface.
4.  **`README.md`**: A top-level file documenting the MVS setup and execution.

***

## 📐 Architectural Constraints & Context

**Role in System**:

* **Backend (`main.py`)**: Simulates the **L4 Core Data Plane** services (ASR, NLP Translator, Animation Engine) and their coordination, exposed via the **L2 API Gateway**. It will contain a single, synchronous endpoint for demonstration, bypassing the Message Broker and WebRTC for MVS simplicity.
* **Frontend (`VoiceToISL.tsx`)**: Simulates the **L1 Client Layer (Recipient/Speaker Mobile App UI)**, handling user input (simulated voice text input) and displaying the simulated output (Text, Gloss, and Avatar Placeholder).

**Dependencies**:

* **Backend**: Must use **FastAPI**, **Pydantic**, and standard Python libraries. No external machine learning models are to be integrated; all L4 logic (ASR, Translation, Gloss-to-Pose) must be implemented with **mock functions** that return *simulated/hardcoded* but architecturally correct data transformations.
* **Frontend**: Must use **React with TypeScript** and a modern CSS framework (e.g., Tailwind CSS or basic CSS) for the quadrant layout. Must use `fetch` or `axios` to communicate with the FastAPI backend.

**Technology Stack**:

* **Backend**: Python $\ge 3.9$ with FastAPI.
* **Frontend**: React $\ge 18$ with TypeScript.

***

## 🛠️ Functional Requirements

### 🎤 Backend (FastAPI - Simulating L4 Voice-to-ISL Flow)

**Inputs**:

* **Endpoint**: `POST /api/v1/translate/voice-to-isl`
* **Request Body (Schema: `VoiceInput` in `schemas.py`)**:
    * `audio_text`: `str` - The simulated transcription of the user's voice input (e.g., "Hello, how are you?"). Must be non-empty.

**Logic Steps (Simulated L4 Microservices)**:

1.  **Step 1: ASR Service Simulation (Transcription)**: Accept `audio_text` as the already-transcribed text token.
2.  **Step 2: NLP Translator Simulation (Text-to-Gloss)**: Create a mock function `text_to_isl_gloss(text_tokens)` that accepts the text and returns a *simulated* ISL Gloss string (e.g., "HELLO HOW YOU?").
3.  **Step 3: Animation Engine Simulation (Gloss-to-Pose)**: Create a mock function `gloss_to_avatar_stream(isl_gloss)` that accepts the gloss and returns a *simulated* video URL or identifier (e.g., a simple string like "avatar\_pose\_stream\_id\_123").
4.  **Step 4: Combine**: The endpoint should orchestrate these three mock steps.

**Outputs/Return**:

* **Success (200 OK - Schema: `ISLOutput` in `schemas.py`)**:
    * `source_text`: `str` - The initial transcribed text (Input).
    * `isl_gloss`: `str` - The simulated ISL Gloss output.
    * `avatar_stream_url`: `str` - The simulated identifier/URL for the avatar stream.
* **Error (400 Bad Request)**: If input validation fails (e.g., empty string).

### 🖥️ Frontend (React/TypeScript - UI & Quadrants)

**Inputs**:

* A simple text input field for the user to type their "voice message" to simulate **Step 1: Capture** and **Step 2: Transcription**.
* A "Translate" button to trigger the API call.

**Logic Steps (User Interface)**:

1.  Display the user interface divided into **four quadrants** as specified in the Conversation Flow.
2.  Upon button click, take the text input and send it to the FastAPI endpoint.
3.  Display the results from the API in the correct quadrants.

**Outputs/Return (Visual Display in Quadrants)**:

| Quadrant | Content Display | Source Data |
| :--- | :--- | :--- |
| **Top-Left** | Voice Recording/Input Simulation | A title/placeholder: "Simulated Voice Input Recording" |
| **Bottom-Left** | Text Tokens | Display the API response's `source_text` (The user's input/transcribed text). |
| **Top-Right** | ISL Gloss Text | Display the API response's `isl_gloss`. |
| **Bottom-Right** | Avatar Rendering | Display a placeholder (e.g., an image or text: "Avatar Video Stream: {`avatar_stream_url`}") for the final signed output. |

***

## 📝 Code & Style Standards (CR/DR Enforcement)

**Style Guide**:

* **Python**: Adhere strictly to **PEP 8** (snake\_case for variables and functions).
* **TypeScript/React**: Use **camelCase** for variables and functions. Components must be **Functional Components**.

**Security**:

* No security or authentication (L3/Session Manager) is required for this MVS, but the API must use **Pydantic** for mandatory input validation.

**Error Handling**:

* **Backend**: Use FastAPI's built-in `HTTPException` for API errors (e.g., for missing input).
* **Frontend**: Use a `try...catch` block around the API call and display a simple error message to the user if the request fails.

**Documentation**:

* Generate **type hints** for all Python functions, methods, and variables.
* Generate **JSDoc-style comments** for all React functional components and their props, describing purpose, parameters, and return types.
* The `README.md` must include instructions on how to start the backend and run the frontend.

***

## 🎯 Non-Functional Requirements

**Testing**:

* **No separate unit test files** are required for this MVS, but the API functions and React component logic should be designed to be easily testable.

**Performance**:

* Latency is not a concern; the focus is on architectural correctness via mock components.