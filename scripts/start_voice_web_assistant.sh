#!/usr/bin/env bash
# ==============================================================================
# ApexPhi-Think-14B: Voice, Web & Advanced Reasoning Assistant Launcher
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PORT="${APEX_VOICE_PORT:-8085}"
HOST="${APEX_VOICE_HOST:-127.0.0.1}"

echo "======================================================================"
echo "  ▲ ApexPhi-Think-14B: Voice, Web & Advanced Reasoning Station        "
echo "======================================================================"

# 1. Python Environment Discovery
PYTHON_BIN="$REPO_ROOT/../.venv-qwen-systems/bin/python3"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

echo "Using Python runtime: $PYTHON_BIN"

# 2. Verify Ollama & Model
echo "Checking Ollama connectivity at http://localhost:11434..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "  ✓ Ollama server online."
    if curl -s http://localhost:11434/api/tags | grep -q "apex-phi-think-14b"; then
        echo "  ✓ apex-phi-think-14b model verified."
    else
        echo "  ⚠ apex-phi-think-14b not found! Creating from Modelfile..."
        ollama create apex-phi-think-14b -f "$REPO_ROOT/Modelfile.apex-phi-think-14b"
    fi
else
    echo "  ✗ Ollama is not running! Starting Ollama is required."
    exit 1
fi

echo ""
echo "Starting Voice & Web Reasoning Server on http://$HOST:$PORT"
echo "Features enabled:"
echo "  • 🧠 Advance Thinking Mode (Fast / Standard / Deep Invariant Proofs)"
echo "  • 🌐 Autonomous Web Search & Retrieval Grounding (DuckDuckGo)"
echo "  • 🎙️ Hands-Free Voice Dictation & Spoken Synthesis"
echo "======================================================================"

cd "$REPO_ROOT"

# Open browser after a brief delay in the background
(
    sleep 2
    if command -v open &> /dev/null; then
        open "http://$HOST:$PORT"
    fi
) &

exec "$PYTHON_BIN" -m web_assistant.backend
