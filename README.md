---
language:
- en
license: mit
library_name: transformers
pipeline_tag: text-generation
tags:
- code
- phi-4
- microsoft
- math
- reasoning
- 36gb-ram
- mlx
- ollama
- algorithmic-coding
base_model: microsoft/phi-4
model_creator: Nilesh Chakraborty
model_name: ApexPhi-14B
inference: true
---

# ⚡ ApexPhi-14B: Mathematical Reasoning & Algorithmic Coding Engine
### Microsoft Phi-4 (14.7B) Architecture | High-Density Synthetic Reasoning | Optimized for 36 GB Unified RAM

[![Model on HF](https://img.shields.io/badge/HF%20Model-nileshc90%2Fapex--phi--14b-green.svg)](https://huggingface.co/nileshc90/apex-phi-14b)
[![GitHub](https://img.shields.io/badge/GitHub-apex--phi--14b-black.svg)](https://github.com/nileshchakraborty/apex-phi-14b)
[![Base Model](https://img.shields.io/badge/Base-Microsoft%20Phi--4%20(14.7B)-blue.svg)](https://huggingface.co/microsoft/phi-4)
[![Memory Profile](https://img.shields.io/badge/M4%20Max%20RAM-0.0%20MB%20Swap-orange.svg)]()

---

## 🏛️ Executive Overview

**ApexPhi-14B** is a high-precision algorithmic coding and mathematical deduction engine built on **Microsoft Research's Phi-4 (14.7B)**. Engineered specifically for high-bandwidth developer workstations and Apple Silicon Macs (M4 Max / M2 Max), it delivers frontier mathematical proofs, complex state machine synthesis, and zero-hallucination code generation.

---

## 🧠 Why ApexPhi-14B as an Algorithmic Backbone?

1. **Unmatched Mathematical & Algorithmic Density**:
   - **MATH-500**: **84.8%** (outperforms many 70B models).
   - **GPQA Diamond**: **56.1%** graduate-level scientific and algorithmic reasoning.
   - Trained on high-density synthetic textbook reasoning data with multi-turn verification.
2. **Zero Non-Western Georestrictions**:
   - Developed in the United States by Microsoft Research under the permissive **MIT License**.
   - Fully open weights for commercial and enterprise deployment.
3. **14.7B Optimal Workstation Footprint**:
   - Fits comfortably in **~10.4 GB RAM** (`Q5_K_M`) or **~8.9 GB RAM** (`Q4_K_M`), leaving over **23 GB of free RAM** on a 36 GB workstation for IDEs, Docker, and build tools with **0.00 MB swap churn**.

---

## 💻 36 GB Unified Memory Allocation

```
+--------------------------------------------------------------------------------+
|                         Total Unified System RAM: 36 GB                        |
+---------------------------------------------------+----------------------------+
|             Active AI Runtime: ~11.0 GB           |    Host Headroom: ~25.0 GB |
|  +---------------------------------------------+  |  +----------------------+  |
|  | ApexPhi-14B (Q5_K_M / Q4_K_M)               |  |  | macOS Kernel (3.5 GB)|  |
|  | ~10.4 GB                                     |  |  +----------------------+  |
|  +---------------------------------------------+  |  | VS Code / IDE (2.5GB)|  |
|  | Q8_0 KV Cache Buffer (~0.6 GB)              |  |  +----------------------+  |
|  +---------------------------------------------+  |  | Docker & Web (6.0 GB)|  |
|                                                   |  +----------------------+  |
|                                                   |  | Build Cache (13.0 GB)|  |
+---------------------------------------------------+----------------------------+
```

---

## 🚀 Quickstart & Deployment

### A. Run with Ollama
```bash
# Build and launch with custom tuned Modelfile
ollama create apex-phi-14b -f Modelfile.apex-phi-14b
ollama run apex-phi-14b
```

### B. High-Throughput Apple Silicon Metal GPU (MLX)
```bash
# Serves local OpenAI-compatible endpoint at http://127.0.0.1:8082/v1
bash scripts/serve_mlx_phi4.sh 8082
```

---

## 🛠️ Continue.dev & VS Code Tab Autocomplete Configuration

Add to your `~/.continue/config.json`:
```json
{
  "models": [
    {
      "title": "ApexPhi-14B (Mathematical Algorithmic Coder)",
      "provider": "ollama",
      "model": "apex-phi-14b",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "ApexPhi-14B Precision Autocomplete",
    "provider": "ollama",
    "model": "apex-phi-14b",
    "apiBase": "http://localhost:11434"
  }
}
```

---

## 🔗 Related Resources
- **ApexCode-14B Model**: [huggingface.co/nileshc90/apex-code-14b-instruct](https://huggingface.co/nileshc90/apex-code-14b-instruct)
- **ApexThink-14B Model**: [huggingface.co/nileshc90/apex-think-14b](https://huggingface.co/nileshc90/apex-think-14b)
- **ApexMistral-22B Model**: [huggingface.co/nileshc90/apex-mistral-22b](https://huggingface.co/nileshc90/apex-mistral-22b)
- **GitHub Repository**: [github.com/nileshchakraborty/apex-phi-14b](https://github.com/nileshchakraborty/apex-phi-14b)
