"""
ApexPhi-Think-14B: Voice, Web & Advanced Thinking Server.
Provides real-time SSE token streaming, web search grounding, voice synthesis (macOS say + Web Speech),
and multi-tier thinking depth control.
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from web_assistant.web_searcher import perform_grounded_web_research

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("apex_phi.voice_web_server")

app = FastAPI(title="ApexPhi-Think Voice & Web Assistant", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/")
MODEL_NAME = os.environ.get("APEX_MODEL", "apex-phi-think-14b")
STATIC_DIR = Path(__file__).parent / "static"

# Track background TTS process
current_tts_process: Optional[subprocess.Popen] = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatStreamRequest(BaseModel):
    messages: List[ChatMessage]
    web_search: bool = True
    think_depth: str = Field(default="standard", description="fast, standard, or deep")
    temperature: Optional[float] = None


class SpeakRequest(BaseModel):
    text: str
    voice: Optional[str] = "Samantha"
    rate: Optional[int] = 190


def clean_text_for_speech(raw_text: str) -> str:
    """Strip <think> reasoning blocks, markdown formatting, and code blocks for spoken audio."""
    # 1. Remove anything before </think> if present
    if "</think>" in raw_text:
        text = raw_text.split("</think>", 1)[1]
    else:
        text = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL)

    # 2. Strip code blocks ``` ... ```
    text = re.sub(r"```[\s\S]*?```", " Code block omitted for audio summary. ", text)
    # 3. Strip inline code ` ... `
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # 4. Strip markdown links [title](url) -> title
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # 5. Strip headers and symbols
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[\*_~]", "", text)
    # 6. Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_installed_macos_voices() -> List[Dict[str, str]]:
    """List available voices from macOS `say -v '?'`."""
    voices = []
    try:
        res = subprocess.run(["say", "-v", "?"], capture_output=True, text=True, check=True)
        for line in res.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(maxsplit=2)
            if len(parts) >= 2:
                name = parts[0]
                lang = parts[1]
                voices.append({"name": name, "lang": lang})
    except Exception as e:
        logger.warning("Could not query macOS voices: %s", e)
        voices = [{"name": "Samantha", "lang": "en_US"}, {"name": "Alex", "lang": "en_US"}]
    return voices


@app.get("/api/health")
def health():
    ollama_ok = False
    model_installed = False
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        if r.status_code == 200:
            ollama_ok = True
            models = [m.get("name", "") for m in r.json().get("models", [])]
            model_installed = any(MODEL_NAME in m for m in models)
    except Exception:
        pass

    return {
        "status": "online",
        "model": MODEL_NAME,
        "ollama_url": OLLAMA_URL,
        "ollama_connected": ollama_ok,
        "model_ready": model_installed,
    }


@app.get("/api/voice/voices")
def list_voices():
    return {"voices": get_installed_macos_voices()}


@app.post("/api/voice/speak")
def speak(req: SpeakRequest):
    global current_tts_process
    # Stop any running utterance
    if current_tts_process and current_tts_process.poll() is None:
        try:
            current_tts_process.terminate()
        except Exception:
            pass

    spoken_text = clean_text_for_speech(req.text)
    if not spoken_text:
        return {"status": "skipped", "message": "No speakable content found"}

    try:
        cmd = ["say"]
        if req.voice:
            cmd.extend(["-v", req.voice])
        if req.rate:
            cmd.extend(["-r", str(req.rate)])
        cmd.append(spoken_text)

        current_tts_process = subprocess.Popen(cmd)
        return {"status": "speaking", "length_chars": len(spoken_text), "voice": req.voice}
    except Exception as e:
        logger.error("TTS invocation error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/stop")
def stop_speech():
    global current_tts_process
    if current_tts_process and current_tts_process.poll() is None:
        try:
            current_tts_process.terminate()
            return {"status": "stopped"}
        except Exception as e:
            logger.warning("Error stopping TTS: %s", e)
    return {"status": "idle"}


@app.post("/api/web/search")
def direct_search(query: str, max_pages: int = 3):
    return perform_grounded_web_research(query, max_pages=max_pages)


async def generate_chat_events(req: ChatStreamRequest) -> AsyncGenerator[str, None]:
    """Stream token-by-token events with real-time thinking status and web research context."""
    user_prompt = ""
    for m in reversed(req.messages):
        if m.role == "user":
            user_prompt = m.content
            break

    # 1. Determine Thinking Budget
    depth_configs = {
        "fast": {"num_predict": 1536, "temp": 0.5},
        "standard": {"num_predict": 3072, "temp": 0.6},
        "deep": {"num_predict": 6144, "temp": 0.7},
    }
    config = depth_configs.get(req.think_depth, depth_configs["standard"])
    temperature = req.temperature if req.temperature is not None else config["temp"]
    num_predict = config["num_predict"]

    # 2. Autonomous Web Grounding Check
    sources = []
    if req.web_search and user_prompt:
        yield f"event: status\ndata: {json.dumps({'message': 'Searching the web for current grounding context...'})}\n\n"
        try:
            research_result = await asyncio.to_thread(perform_grounded_web_research, user_prompt, 3)
            sources = research_result.get("sources", [])
            context_text = research_result.get("context_text", "")
            if sources:
                yield f"event: sources\ndata: {json.dumps({'sources': sources})}\n\n"
                # Inject web context into system message
                web_context_prompt = (
                    f"\n\n[EXTERNAL LIVE WEB SEARCH CONTEXT]\n"
                    f"{context_text}\n"
                    f"[INSTRUCTIONS: Ground facts in the web sources above. Cite them as [Source N: Title].]"
                )
                # Append to last user message or add system prompt
                req.messages[-1].content += web_context_prompt
        except Exception as e:
            logger.warning("Web search grounding error: %s", e)

    yield f"event: status\ndata: {json.dumps({'message': f'Starting {req.think_depth.upper()} reasoning pipeline...'})}\n\n"

    # 3. Call Ollama Chat Stream
    ollama_payload = {
        "model": MODEL_NAME,
        "messages": [m.model_dump() for m in req.messages],
        "stream": True,
        "options": {
            "temperature": temperature,
            "top_p": 0.95,
            "min_p": 0.05,
            "num_predict": num_predict,
            "num_ctx": 16384,
            "repeat_penalty": 1.10,
        },
    }

    t0 = time.perf_counter()
    in_think_block = True
    full_response = ""
    thinking_buffer = ""
    answer_buffer = ""

    try:
        resp = requests.post(f"{OLLAMA_URL}/api/chat", json=ollama_payload, stream=True, timeout=300)
        resp.raise_for_status()

        for line in resp.iter_lines():
            if not line:
                continue
            try:
                chunk = json.loads(line.decode("utf-8"))
            except Exception:
                continue

            msg_chunk = chunk.get("message", {}).get("content", "")
            full_response += msg_chunk

            if in_think_block:
                if "</think>" in msg_chunk or "</think>" in full_response:
                    in_think_block = False
                    # Split transition chunk
                    parts = msg_chunk.split("</think>", 1)
                    think_part = parts[0]
                    answer_part = parts[1] if len(parts) > 1 else ""

                    if think_part:
                        yield f"event: think_token\ndata: {json.dumps({'token': think_part})}\n\n"
                    yield f"event: think_end\ndata: {json.dumps({'elapsed': round(time.perf_counter() - t0, 2)})}\n\n"
                    if answer_part:
                        yield f"event: answer_token\ndata: {json.dumps({'token': answer_part})}\n\n"
                else:
                    yield f"event: think_token\ndata: {json.dumps({'token': msg_chunk})}\n\n"
            else:
                yield f"event: answer_token\ndata: {json.dumps({'token': msg_chunk})}\n\n"

            if chunk.get("done"):
                total_time = round(time.perf_counter() - t0, 2)
                eval_count = chunk.get("eval_count", 0)
                eval_duration = chunk.get("eval_duration", 0) / 1e9
                speed = round(eval_count / eval_duration, 1) if eval_duration > 0 else 0

                spoken_summary = clean_text_for_speech(full_response)
                yield f"event: done\ndata: {json.dumps({'total_time': total_time, 'tokens': eval_count, 'speed': speed, 'spoken_summary': spoken_summary})}\n\n"
                break

    except Exception as e:
        logger.exception("Error in Ollama chat streaming")
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"


@app.post("/api/chat/stream")
async def chat_stream(req: ChatStreamRequest):
    return StreamingResponse(
        generate_chat_events(req),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# Serve Static UI
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    idx_file = STATIC_DIR / "index.html"
    if idx_file.exists():
        return FileResponse(str(idx_file))
    return JSONResponse({"status": "ApexPhi-Think-14B Voice & Web Backend Online"})


def run():
    port = int(os.environ.get("APEX_VOICE_PORT", 8085))
    host = os.environ.get("APEX_VOICE_HOST", "127.0.0.1")
    logger.info("Starting ApexPhi-Think Voice & Web Server on http://%s:%d", host, port)
    uvicorn.run("web_assistant.backend:app", host=host, port=port, reload=False, log_level="info")


if __name__ == "__main__":
    run()
