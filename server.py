# import os
# import sys
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from dotenv import load_dotenv

# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS

# from pipecat.frames.frames import TextFrame
# from pipecat.pipeline.pipeline import Pipeline
# from pipecat.pipeline.runner import PipelineRunner
# from pipecat.pipeline.task import PipelineTask
# # from pipecat.services.openai import OpenAILLMService
# from pipecat.services.openai.llm import OpenAILLMService
# from pipecat.transports.websocket.fastapi import (
#     FastAPIWebsocketTransport,
#     FastAPIWebsocketParams
# )

# load_dotenv()
# GH_TOKEN = os.getenv("GITHUB_TOKEN")

# if not GH_TOKEN:
#     print("❌ Error: GITHUB_TOKEN missing from .env file.")
#     sys.exit(1)

# app = FastAPI(title="Real-Time Voice RAG Agent Backend")

# # 1. Initialize Local FAISS and Hugging Face Vector Store
# print("⏳ Loading FAISS Index and Hugging Face Model into server memory...")
# embeddings_model = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2",
#     model_kwargs={"device": "cpu"}
# )

# # Load local DB with safe evaluation
# vector_db = FAISS.load_local("faiss_index", embeddings_model, allow_dangerous_deserialization=True)
# retriever = vector_db.as_retriever(search_kwargs={"k": 2})

# def query_rag_knowledge(query: str) -> str:
#     """Helper function to fetch matching document snippets."""
#     docs = retriever.invoke(query)
#     context = "\n".join([doc.page_content for doc in docs])
#     return context if context.strip() else "No relevant context found in custom documents."

# # Define the structured tool definition for Pipecat / GPT-4o function calling
# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "query_knowledge_base",
#             "description": "Consult this internal database to answer questions about specific system passkeys, manual details, or custom documentation.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "query": {
#                         "type": "string",
#                         "description": "The search query extracted from the user's speech."
#                     }
#                 },
#                 "required": ["query"],
#             },
#         },
#     }
# ]

# # 2. Tool handler callback for the LLM Service
# async def handle_tool_call(llm, model, name, args, app_message_context):
#     if name == "query_knowledge_base":
#         user_query = args.get("query")
#         print(f"🔍 RAG Tool Triggered! Querying FAISS for: '{user_query}'")
#         context_result = query_rag_knowledge(user_query)
        
#         # Inject the retrieved context back into the conversation context frame
#         return [{"role": "tool", "content": f"Retrieved Context:\n{context_result}"}]
#     return None

# # 3. WebSocket Route for Real-Time Streaming Audio
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     print("🤝 Client connected over WebSocket connection.")

#     # Configure Pipecat WebSocket Transport
#     transport = FastAPIWebsocketTransport(
#         websocket=websocket,
#         params=FastAPIWebsocketParams(
#             audio_out_enabled=True,
#             audio_in_enabled=True
#         )
#     )

#     # Initialize OpenAI Service re-routed to GitHub Free Models
#     llm_service = OpenAILLMService(
#         api_key=GH_TOKEN,
#         model="gpt-4o",
#         base_url="https://models.inference.ai.azure.com"
#     )

#     # Base System Prompt telling the agent how to act and behave
#     sys_prompt = (
#         "You are a helpful, real-time voice-activated AI support agent. "
#         "You speak concisely, naturally, and straight to the point because your responses are converted to speech. "
#         "When asked about specific instructions, configuration metrics, or system passkeys, ALWAYS call the "
#         "'query_knowledge_base' tool function to fetch reality-checked facts before guessing."
#     )

#     # Clean and Proper Pipecat Context Initialization (Passes tools here instead of .register_tools)
#     # context = LLMService(
#     #     messages=[{"role": "system", "content": sys_prompt}], 
#     #     tools=tools
#     # )
#     # context_notifier = llm_service.create_context_notifier(context)

#     # Bind the tool execution callback directly to the service mapping
#     llm_service.register_function("query_knowledge_base", handle_tool_call)

#     # Construct the sequential execution pipeline
#     pipeline = Pipeline([
#         transport.input(),
#         llm_service,
#         transport.output()
#     ])

#     # Wire up the background pipeline runner task
#     runner = PipelineRunner()
#     task = PipelineTask(pipeline)

#     # Let the agent start the conversation with an greeting audio cue
#     @transport.event_handler("on_client_connected")
#     async def on_client_connected(transport, client):
#         print("🔊 Voice session started. Injecting initial welcome greeting...")
#         await task.queue_frame(OpenAILLMService([{"role": "user", "content": "Introduce yourself briefly."}]))

#     try:
#         # Run the streaming task loop until connection closure
#         await runner.run(task)
#     except WebSocketDisconnect:
#         print("👋 Client disconnected safely from voice channel.")
#     except Exception as e:
#         print(f"⚠️ Pipeline execution warning/error: {e}")

# if __name__ == "__main__":
#     import uvicorn
#     # Fire up our local live server on port 8000
#     uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

















# import os
# import sys
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from dotenv import load_dotenv

# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS

# from pipecat.frames.frames import LLMFullResponseStartFrame, LLMFullResponseEndFrame
# from pipecat.pipeline.pipeline import Pipeline
# from pipecat.pipeline.runner import PipelineRunner
# from pipecat.pipeline.task import PipelineTask

# from pipecat.services.openai.llm import OpenAILLMService
# from pipecat.services.llm_service import FunctionCallParams

# from pipecat.transports.websocket.fastapi import (
#     FastAPIWebsocketTransport,
#     FastAPIWebsocketParams
# )

# load_dotenv()
# GH_TOKEN = os.getenv("GITHUB_TOKEN")

# if not GH_TOKEN:
#     print("❌ Error: GITHUB_TOKEN missing from .env file.")
#     sys.exit(1)

# app = FastAPI(title="Real-Time Voice RAG Agent Backend")

# # -----------------------------
# # 1. VECTOR STORE (FAISS)
# # -----------------------------
# print("⏳ Loading FAISS Index...")
# embeddings_model = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2",
#     model_kwargs={"device": "cpu"}
# )

# vector_db = FAISS.load_local(
#     "faiss_index",
#     embeddings_model,
#     allow_dangerous_deserialization=True
# )

# retriever = vector_db.as_retriever(search_kwargs={"k": 3})


# def query_rag_knowledge(query: str) -> str:
#     docs = retriever.invoke(query)
#     return "\n".join([doc.page_content for doc in docs]) or "No relevant context found."


# # -----------------------------
# # 2. TOOL HANDLER (CORRECT Pipecat 1.3.0 STYLE)
# # -----------------------------
# async def handle_tool_call(params: FunctionCallParams):
#     query = params.arguments.get("query", "")

#     print(f"🔍 RAG Tool Triggered: {query}")

#     result = query_rag_knowledge(query)

#     # IMPORTANT: Pipecat expects result via callback dict
#     await params.result_callback(
#         {
#             "role": "tool",
#             "content": result
#         }
#     )


# # -----------------------------
# # 3. FASTAPI APP
# # -----------------------------
# app = FastAPI(title="Voice RAG Agent")


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     print("🤝 Client connected")

#     # -----------------------------
#     # Transport
#     # -----------------------------
#     transport = FastAPIWebsocketTransport(
#         websocket=websocket,
#         params=FastAPIWebsocketParams(
#             audio_in_enabled=True,
#             audio_out_enabled=True
#         )
#     )

#     # -----------------------------
#     # LLM SERVICE
#     # -----------------------------
#     llm = OpenAILLMService(
#         api_key=GH_TOKEN,
#         model="gpt-4o",
#         base_url="https://models.inference.ai.azure.com"
#     )

#     # Register tool (CORRECT API)
#     llm.register_function("query_knowledge_base", handle_tool_call)

#     # IMPORTANT SYSTEM PROMPT
#     system_prompt = """
# You are a real-time voice assistant.

# RULES:
# - Always use query_knowledge_base tool for questions about documents, definitions, or RAG content.
# - Never guess when tool is available.
# - Keep answers short and spoken-friendly.
# """

#     llm.append_system_instruction(system_prompt)

#     # -----------------------------
#     # PIPELINE
#     # -----------------------------
#     pipeline = Pipeline([
#         transport.input(),
#         llm,
#         transport.output()
#     ])

#     task = PipelineTask(pipeline)
#     runner = PipelineRunner()

#     # -----------------------------
#     # START EVENT
#     # -----------------------------
#     @transport.event_handler("on_client_connected")
#     async def on_client_connected(transport, client):
#         print("🔊 Session started")

#         await task.queue_frame(
#             LLMFullResponseStartFrame()
#         )

#     # -----------------------------
#     # RUN
#     # -----------------------------
#     try:
#         await runner.run(task)

#     except WebSocketDisconnect:
#         print("👋 Client disconnected")

#     except Exception as e:
#         print(f"⚠️ Error: {e}")


# # -----------------------------
# # MAIN
# # -----------------------------
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
















import os
import sys
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Pipecat core imports (CORRECT for 1.3)
from pipecat.frames.frames import LLMMessagesAppendFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask

from pipecat.services.llm_service import FunctionCallParams
from pipecat.services.openai.llm import OpenAILLMService

# from pipecat.services.stt_service import STTService
from pipecat.services.whisper.stt import WhisperSTTService
# from pipecat.services.tts_service import TTSService
from pipecat.services.kokoro.tts import KokoroTTSService
from pipecat.transports.websocket.fastapi import (
    FastAPIWebsocketTransport,
    FastAPIWebsocketParams,
)

load_dotenv()
GH_TOKEN = os.getenv("GITHUB_TOKEN")

if not GH_TOKEN:
    print("❌ Missing GITHUB_TOKEN")
    sys.exit(1)

app = FastAPI(title="Pipecat Voice RAG Agent")

# -----------------------------
# FAISS + Embeddings
# -----------------------------
print("⏳ Loading FAISS index...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

vector_db = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vector_db.as_retriever(search_kwargs={"k": 2})


def query_rag_knowledge(query: str) -> str:
    docs = retriever.invoke(query)
    return "\n".join([d.page_content for d in docs]) or "No relevant context found."


# -----------------------------
# TOOL HANDLER (Pipecat 1.3 way)
# -----------------------------
async def handle_tool_call(params: FunctionCallParams):
    if params.function_name != "query_knowledge_base":
        return

    user_query = params.arguments.get("query", "")
    print(f"🔍 RAG TOOL: {user_query}")

    result = query_rag_knowledge(user_query)

    # IMPORTANT: return via callback (Pipecat 1.3)
    await params.result_callback(
        {
            "role": "tool",
            "content": f"Retrieved Context:\n{result}",
        }
    )


# -----------------------------
# FASTAPI WS
# -----------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🤝 Client connected")

    transport = FastAPIWebsocketTransport(
        websocket=websocket,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            audio_in_sample_rate=16000,
            audio_out_sample_rate=16000,
        ),
    )

    # STT (Whisper local)
    stt = WhisperSTTService()

    # LLM (GitHub OpenAI-compatible)
    llm = OpenAILLMService(
        api_key=GH_TOKEN,
        model="gpt-4o",
        base_url="https://models.inference.ai.azure.com",
    )

    # TTS (FIXED: EdgeTTSService DOES NOT exist in your version)
    tts = KokoroTTSService(
        voice="af-sarah",
    )

        
    # Register tool (CORRECT API)
    llm.register_function("query_knowledge_base", handle_tool_call)

    # System prompt
    system_prompt = (
        "You are a real-time voice AI assistant. "
        "Use tools for factual retrieval before guessing."
    )

    # Pipeline
    pipeline = Pipeline([
        transport.input(),
        stt,
        llm,
        tts,
        transport.output(),
    ])

    runner = PipelineRunner()
    task = PipelineTask(pipeline)

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        print("🔊 Session started")

        await task.queue_frame(
            LLMMessagesAppendFrame([
                {
                    "role": "user",
                    "content": system_prompt + " Say hello briefly.",
                }
            ])
        )

    try:
        await runner.run(task)

    except WebSocketDisconnect:
        print("👋 Disconnected")

    except Exception as e:
        print(f"⚠️ Error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)