#!/usr/bin/env python3
"""
ApexPhi-Think-14B: Terminal CLI with Voice, Web Grounding, and Advanced Reasoning.

Usage:
    python scripts/apex_think_interactive.py
    python scripts/apex_think_interactive.py --voice --web --depth deep
    python scripts/apex_think_interactive.py --prompt "Prove that sqrt(2) is irrational" --voice
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from typing import Any, Dict, List

import requests

# Add repo root to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from web_assistant.web_searcher import perform_grounded_web_research

MODEL_NAME = os.getenv("APEX_MODEL", "apex-phi-think-14b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")

# ANSI Colors
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_PURPLE = "\033[38;5;141m"
C_CYAN = "\033[38;5;51m"
C_BLUE = "\033[38;5;39m"
C_GREEN = "\033[38;5;48m"
C_YELLOW = "\033[38;5;220m"
C_RED = "\033[38;5;203m"


def clean_text_for_speech(raw_text: str) -> str:
    """Strip <think> blocks and code formatting for speech synthesis."""
    if "</think>" in raw_text:
        text = raw_text.split("</think>", 1)[1]
    else:
        text = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL)

    text = re.sub(r"```[\s\S]*?```", " Code block omitted for voice summary. ", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[\*_~]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def speak_macos(text: str, voice: str = "Samantha"):
    """Speak text on macOS using /usr/bin/say in background."""
    spoken = clean_text_for_speech(text)
    if not spoken:
        return
    try:
        subprocess.Popen(["say", "-v", voice, "-r", "190", spoken])
    except Exception as e:
        print(f"{C_RED}[Voice Error]{C_RESET} {e}", file=sys.stderr)


def query_think_stream(
    messages: List[Dict[str, str]],
    web_search: bool = True,
    depth: str = "standard",
    voice: bool = False,
    voice_name: str = "Samantha"
) -> str:
    depth_configs = {
        "fast": {"num_predict": 1536, "temp": 0.5},
        "standard": {"num_predict": 3072, "temp": 0.6},
        "deep": {"num_predict": 6144, "temp": 0.7},
    }
    cfg = depth_configs.get(depth, depth_configs["standard"])

    user_query = messages[-1]["content"]

    # 1. Web Grounding
    if web_search:
        print(f"{C_BLUE}🌐 Autonomous Web Search & Retrieval Grounding...{C_RESET}")
        try:
            res = perform_grounded_web_research(user_query, max_pages=3)
            sources = res.get("sources", [])
            context = res.get("context_text", "")
            if sources:
                print(f"{C_GREEN}✓ Retrieved {len(sources)} sources:{C_RESET}")
                for s in sources:
                    print(f"  [{s['id']}] {s['title']} ({s['url']})")
                grounding_prompt = f"\n\n[LIVE WEB SEARCH CONTEXT]\n{context}\n[Cite sources as [Source N: Title]]"
                messages[-1]["content"] += grounding_prompt
        except Exception as e:
            print(f"{C_YELLOW}⚠ Web search warning: {e}{C_RESET}")

    # 2. Call Ollama Stream
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": True,
        "options": {
            "temperature": cfg["temp"],
            "top_p": 0.95,
            "min_p": 0.05,
            "num_predict": cfg["num_predict"],
            "num_ctx": 16384,
            "repeat_penalty": 1.10
        }
    }

    print(f"\n{C_PURPLE}🧠 [ApexPhi-Think-14B Reasoning Process ({depth.upper()})]{C_RESET}")
    print(f"{C_DIM}┌" + "─" * 70)

    t0 = time.perf_counter()
    full_response = ""
    in_think_block = True

    try:
        resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, stream=True, timeout=300)
        resp.raise_for_status()

        for line in resp.iter_lines():
            if not line:
                continue
            chunk = json.loads(line.decode("utf-8"))
            tok = chunk.get("message", {}).get("content", "")
            full_response += tok

            if in_think_block:
                if "</think>" in tok or "</think>" in full_response:
                    in_think_block = False
                    parts = tok.split("</think>", 1)
                    if parts[0]:
                        sys.stdout.write(f"{C_PURPLE}{parts[0]}{C_RESET}")
                    elapsed_think = round(time.perf_counter() - t0, 2)
                    sys.stdout.write(f"\n{C_DIM}└" + "─" * 70 + f"{C_RESET}\n")
                    print(f"{C_PURPLE}✓ Completed Reasoning in {elapsed_think}s{C_RESET}\n")
                    print(f"{C_BOLD}{C_CYAN}💬 [Verified Solution & Synthesis]{C_RESET}")
                    if len(parts) > 1 and parts[1]:
                        sys.stdout.write(parts[1])
                        sys.stdout.flush()
                else:
                    sys.stdout.write(f"{C_PURPLE}{tok}{C_RESET}")
                    sys.stdout.flush()
            else:
                sys.stdout.write(tok)
                sys.stdout.flush()

            if chunk.get("done"):
                total_time = round(time.perf_counter() - t0, 2)
                eval_count = chunk.get("eval_count", 0)
                eval_dur = chunk.get("eval_duration", 0) / 1e9
                speed = round(eval_count / eval_dur, 1) if eval_dur > 0 else 0
                print(f"\n\n{C_DIM}───────────────────────────────────────────────────────{C_RESET}")
                print(f"{C_CYAN}⚡ Finished in {total_time}s | {eval_count} tokens | {speed} tok/s{C_RESET}")
                break

    except Exception as e:
        print(f"\n{C_RED}Error during chat stream: {e}{C_RESET}", file=sys.stderr)

    if voice:
        print(f"{C_BLUE}🔊 Playing Voice Summary via macOS ({voice_name})...{C_RESET}")
        speak_macos(full_response, voice=voice_name)

    return full_response


def main():
    parser = argparse.ArgumentParser(description="ApexPhi-Think-14B Voice, Web & Reasoning CLI")
    parser.add_argument("--prompt", type=str, help="Single-shot prompt to run")
    parser.add_argument("--web", action="store_true", default=True, help="Enable autonomous web search grounding (default: True)")
    parser.add_argument("--no-web", dest="web", action="store_false", help="Disable web search grounding")
    parser.add_argument("--voice", action="store_true", help="Enable macOS spoken audio narration for response summaries")
    parser.add_argument("--voice-name", type=str, default="Samantha", help="macOS voice name (e.g. Samantha, Alex, Daniel)")
    parser.add_argument("--depth", choices=["fast", "standard", "deep"], default="standard", help="Thinking depth & reasoning budget")
    args = parser.parse_args()

    print(f"{C_BOLD}{C_CYAN}======================================================================{C_RESET}")
    print(f"{C_BOLD}{C_BLUE}▲ ApexPhi-Think-14B: Voice, Web & Advanced Thinking Engine{C_RESET}")
    print(f"  Model: {MODEL_NAME} | Architecture: Microsoft Phi-4 (14.7B)")
    print(f"  Web Search: {'ON' if args.web else 'OFF'} | Voice Output: {'ON (' + args.voice_name + ')' if args.voice else 'OFF'} | Depth: {args.depth.upper()}")
    print(f"{C_BOLD}{C_CYAN}======================================================================{C_RESET}\n")

    if args.prompt:
        messages = [{"role": "user", "content": args.prompt}]
        query_think_stream(messages, web_search=args.web, depth=args.depth, voice=args.voice, voice_name=args.voice_name)
        return

    # Interactive REPL
    history: List[Dict[str, str]] = []
    print(f"{C_YELLOW}Type your question/theorem, '/voice' to toggle audio, '/depth <fast|standard|deep>', or 'exit':{C_RESET}\n")

    current_voice = args.voice
    current_depth = args.depth
    current_web = args.web

    while True:
        try:
            user_in = input(f"{C_BOLD}{C_GREEN}User ➔ {C_RESET}").strip()
            if not user_in:
                continue
            if user_in.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break
            if user_in.startswith("/voice"):
                current_voice = not current_voice
                print(f"Voice output toggled: {'ENABLED' if current_voice else 'DISABLED'}")
                continue
            if user_in.startswith("/web"):
                current_web = not current_web
                print(f"Web grounding toggled: {'ENABLED' if current_web else 'DISABLED'}")
                continue
            if user_in.startswith("/depth"):
                parts = user_in.split()
                if len(parts) > 1 and parts[1] in ["fast", "standard", "deep"]:
                    current_depth = parts[1]
                    print(f"Thinking depth set to: {current_depth.upper()}")
                else:
                    print("Usage: /depth [fast | standard | deep]")
                continue

            history.append({"role": "user", "content": user_in})
            resp = query_think_stream(
                history,
                web_search=current_web,
                depth=current_depth,
                voice=current_voice,
                voice_name=args.voice_name
            )
            history.append({"role": "assistant", "content": resp})
            print("\n")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()
