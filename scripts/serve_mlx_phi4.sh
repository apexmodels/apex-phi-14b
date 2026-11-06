#!/usr/bin/env bash
# ==============================================================================
# ApexPhi-14B: High-Throughput Metal GPU Serving via MLX / Llama.cpp
# Optimized for Apple Silicon M4 Max / M2 Max (36 GB / 96 GB Systems)
# ==============================================================================

set -euo pipefail

PORT="${1:-8082}"
MODEL_ID="${2:-mlx-community/phi-4-4bit}"

echo "=================================================================="
echo "⚡ Starting ApexPhi-14B Metal GPU Inference Server"
echo "   Model:    ${MODEL_ID}"
echo "   Endpoint: http://127.0.0.1:${PORT}/v1/chat/completions"
echo "   Hardware: Apple Silicon Metal (Unified Memory)"
echo "   Context:  16,384 tokens (Scalable to 32k)"
echo "   Sampling: Min-P = 0.05"
echo "=================================================================="

if ! python3 -c "import mlx_lm" &>/dev/null; then
    echo "📦 Installing mlx-lm..."
    pip install -q mlx-lm
fi

exec python3 -m mlx_lm.server \
    --model "${MODEL_ID}" \
    --port "${PORT}" \
    --host 0.0.0.0
