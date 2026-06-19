readme_content = """# Production-Ready Real-Time Voice AI Agent with Local RAG

We have built a production-ready, ultra-low latency Real-Time Voice AI Agent that integrates **Retrieval-Augmented Generation (RAG)** with streaming voice pipelines. The system enables natural, spoken conversations with an AI assistant that can access custom local knowledge bases via vector databases for instantaneous information retrieval. 

Crucially, this entire architecture is designed to run **100% on Free Tiers and local open-source models**, eliminating the need for premium cloud API subscriptions during development and prototyping.

---

## 🏗️ System Architecture & Data Flow

[ User Speaks ] ──(Audio Stream)──> [ React Frontend ]
│
(WebSocket Stream)
▼
[ FastAPI Backend ]
│
(Pipecat Pipeline)
│
┌────────────────────────────────────────┴────────────────────────────────────────┐
▼                                                                                 ▼
[ STT Engine ] ──> [ Text Prompt ] ──> [ MongoDB Vector Search ]                 [ TTS Engine ]
│                                     ▲
(Context Found)                              │
▼                                     │
[ GitHub Models (GPT-4o) ] ──(Text Stream)───────┘

1. **Audio Streaming:** The React frontend captures user voice via the Web Audio API, encodes it into 16-bit Signed Linear PCM blocks, and streams it continuously over an active WebSocket connection.
2. **Orchestration Framework:** The FastAPI server uses **Pipecat** to manage asynchronous frames, voice activity detection (VAD), and low-latency audio pipes.
3. **Speech-to-Text (STT):** Raw incoming audio data is transcribed in real-time into text via **Whisper STT**.
4. **Local Vector Search (RAG):** The text is parsed by the pipeline. If the user asks about specific system details, the agent invokes a custom tool mapping that performs a similarity search against a local **FAISS Vector Index** using **Hugging Face Sentence-Transformer Embeddings (`all-MiniLM-L6-v2`)**.
5. **Inference & Reasoning:** The retrieved document context combined with the system prompt is transmitted to the free **GitHub Models Registry (`gpt-4o`)** utilizing a standard OpenAI-compatible gateway.
6. **Text-to-Speech (TTS):** As tokens stream back, they are immediately fed into **EdgeTTS**, generating natural-sounding synthesized audio chunks.
7. **Audio Playback:** Raw speech frames are piped back through the WebSocket connection and natively decoded by the browser client's speaker context.

---

## 🛠️ Tech Stack & Dependencies

### Backend
* **FastAPI & Uvicorn:** High-performance, asynchronous web server framework.
* **Pipecat AI (`pipecat-ai[whisper,edge]`, `pipecat-ai-openai`):** Production framework for real-time streaming voice agents.
* **FAISS (CPU variant):** Facebook AI Similarity Search for dense vector clustering.
* **LangChain Core & HuggingFace Integrations:** Wrappers to orchestrate indices and model pipelines.

### Frontend
* **React (v18+) & TypeScript:** Standard UI development framework.
* **Vite:** Next-generation frontend tooling for optimized compilation and live-reloads.
* **Web Audio API:** Native browser components for granular PCM recording and audio frame processing.

---

## 🚀 Step-by-Step Setup Guide

### Prerequisites
* Ensure you have **Python 3.10+** and **Node.js (v18+)** installed.
* Generate a free **GitHub Personal Access Token (PAT)** with permission to read models (`models:read`) via your GitHub profile settings.

### 1. Repository Core & Environment Setup
Clone or create your project workspace and configure your environment variables:

```bash
mkdir voice-ai-agent && cd voice-ai-agent

Create a .env file in the root backend directory:

2. Backend Setup & Ingestion

# Windows
python -m venv voiceai
.\\voiceai\\Scripts\\Activate.ps1

# Linux / macOS
python3 -m venv voiceai
source voiceai/bin/activate

# Install requirements
pip install fastapi uvicorn python-dotenv pypdf langchain-huggingface langchain-community sentence-transformers
pip install "pipecat-ai[whisper,edge]" pipecat-ai-openai


Drop your custom data documents (e.g., policy PDFs, manuals, or technical text notes) into the workspace directory. Run the ingestion pipeline to extract, chunk, embed, and store your facts into the local vector index:

python ingest_local.py

(This creates a faiss_index/ directory storing localized vector spaces).

Launch the live real-time server:
python server.py

3. Frontend Setup

npm create vite@latest voice-frontend -- --template react-ts
cd voice-frontend
npm install

Replace the boilerplate inside src/App.tsx with our standard PCM voice-streaming client interface code. Then boot the client:
    
npm run dev
Open http://localhost:5173/ in your browser to begin testing.


🧪 Operational Testing Matrix
Once connected, we can comprehensively evaluate the system using three testing boundaries:

RAG Knowledge Verification: Ask specifically about data contained within your ingested files (e.g., "What is the secret system passkey?"). Observe the server logs to verify that the query_knowledge_base tool function triggers a FAISS vector matching execution before responding.

Latency & Conversational Performance: Engage in rapid, short conversational dialogs (e.g., "Hello, count to three quickly.") to measure the end-to-end processing speeds of Whisper, GPT-4o, and EdgeTTS.

Prompt Boundary Constraints: Ask the agent to formulate long essays or stories. Verify that it respects the strict system prompt rules requiring responses to be highly concise and optimized for spoken, auditory tracking.