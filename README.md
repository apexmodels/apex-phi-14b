---
language:
- en
license: mit
library_name: transformers
pipeline_tag: text-generation
tags:
- code
- reasoning
- phi-4
- microsoft
- math
- 36gb-ram
- mlx
- ollama
- algorithmic-coding
base_model: microsoft/phi-4
model_creator: Nilesh Chakraborty
model_name: ApexPhi-14B
inference: true
---

# ⚡ ApexPhi-14B: Dual-Edition Workstation Suite (Coder & Think)
### Microsoft Phi-4 (14.7B) Architecture | Mathematical Invariants & Formal Proofs | Optimized for 36 GB Unified RAM

[![Model on HF](https://img.shields.io/badge/HF%20Model-nileshc90%2Fapex--phi--14b-green.svg)](https://huggingface.co/nileshc90/apex-phi-14b)
[![GitHub](https://img.shields.io/badge/GitHub-apex--phi--14b-black.svg)](https://github.com/nileshchakraborty/apex-phi-14b)
[![Base Model](https://img.shields.io/badge/Base-Microsoft%20Phi--4%20(14.7B)-blue.svg)](https://huggingface.co/microsoft/phi-4)
[![Memory Profile](https://img.shields.io/badge/M4%20Max%20RAM-0.0%20MB%20Swap-orange.svg)]()

---

## 🏛️ Executive Overview

**ApexPhi-14B** delivers a specialized **dual-edition intelligence architecture** built on **Microsoft Research's Phi-4 (14.7B)**, optimized for developer workstations and Apple Silicon Macs (M4 Max / M2 Max):

1. **⚡ ApexPhi-Coder-14B**:
   - Specialized in **high-precision algorithmic coding, AST-verified syntax, and type safety**.
   - Direct, deterministic execution with zero conversational fluff.
   - Zero-Assumption Invariant: strict schema and boundary verification.
   - Sampling: `temperature 0.2`, `top_p 0.95`, `min_p 0.04`.

2. **🧠 ApexPhi-Think-14B**:
   - Specialized in **deep mathematical theorem proving, combinatorial logic, and state-machine transitions**.
   - Employs formal step-by-step invariant derivations inside `<think> ... </think>` before stating proofs or code.
   - Formal verification guardrails: mathematically audits parity, induction steps, and boundary states.
   - Sampling: `temperature 0.6`, `top_p 0.95`, `min_p 0.05`.

Both editions run within **~10.4 GB RAM** (`Q5_K_M`) or **~8.9 GB RAM** (`Q4_K_M`), leaving over **23 GB of free host RAM** on a 36 GB workstation for IDEs, Docker, and developer tools with **0.00 MB swap churn**.

---

## 🧠 Why ApexPhi-14B as an Algorithmic Backbone?

1. **Unmatched Mathematical & Algorithmic Density**:
   - **MATH-500**: **84.8%** (outperforms many 70B models).
   - **GPQA Diamond**: **56.1%** graduate-level scientific and algorithmic reasoning.
   - Trained on high-density synthetic textbook reasoning data with multi-turn verification.
2. **Zero Non-Western Georestrictions**:
   - Developed in the United States by Microsoft Research under the permissive **MIT License**.
   - Fully open weights for commercial and enterprise deployment.
3. **Dynamic Min-P Sampling Cutoff**:
   - Dynamically prunes low-probability hallucinated tail tokens relative to the top token's confidence, ensuring high logical coherence.

---

## 💻 36 GB Unified Memory Allocation

```
+--------------------------------------------------------------------------------+
|                         Total Unified System RAM: 36 GB                        |
+---------------------------------------------------+----------------------------+
|             Active AI Runtime: ~11.0 GB           |    Host Headroom: ~25.0 GB |
|  +---------------------------------------------+  |  +----------------------+  |
|  | ApexPhi-14B (Coder / Think)                 |  |  | macOS Kernel (3.5 GB)|  |
|  | ~10.4 GB (0.0 MB Swap Churn)                |  |  +----------------------+  |
|  +---------------------------------------------+  |  | VS Code / IDE (2.5GB)|  |
|  | Q8_0 KV Cache Buffer (~0.6 GB)              |  |  +----------------------+  |
|  +---------------------------------------------+  |  | Docker & Web (6.0 GB)|  |
|                                                   |  +----------------------+  |
|                                                   |  | Build Cache (13.0 GB)|  |
+---------------------------------------------------+----------------------------+
```

---

## 🚀 1-Click Run Commands

### A. Run with Ollama

```bash
# 1. Run the High-Precision Algorithmic Coder Edition:
ollama run apex-phi-coder-14b

# 2. Run the Deep Mathematical Proof / Think Edition:
ollama run apex-phi-think-14b
```

### B. Interactive Voice, Web Grounding & Advanced Thinking Station (Web UI)

Launch the full-featured browser studio with hands-free microphone dictation, spoken audio synthesis, live DuckDuckGo web grounding, and collapsible `<think>` chain-of-thought accordion:

```bash
# Launch Voice & Web Thinking Assistant on http://127.0.0.1:8085
bash scripts/start_voice_web_assistant.sh
```

### C. Terminal CLI with Voice & Web Grounding

```bash
# Interactive REPL with Web Search, Voice Output & Deep Reasoning:
python scripts/apex_think_interactive.py --voice --web --depth deep

# Single-shot prompt with macOS audio read-aloud:
python scripts/apex_think_interactive.py --prompt "Prove that sqrt(2) is irrational" --voice
```

### D. High-Throughput Apple Silicon Metal GPU (MLX)
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
      "title": "ApexPhi-Coder-14B (High-Precision Algorithmic Coder)",
      "provider": "ollama",
      "model": "apex-phi-coder-14b",
      "apiBase": "http://localhost:11434"
    },
    {
      "title": "ApexPhi-Think-14B (Mathematical Proofs & CoT)",
      "provider": "ollama",
      "model": "apex-phi-think-14b",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "ApexPhi-Coder-14B Precision Autocomplete",
    "provider": "ollama",
    "model": "apex-phi-coder-14b",
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
