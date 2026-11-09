"""
Comprehensive Test Suite for ApexPhi-Think-14B:
- Voice synthesis text cleanup
- Web search and grounding pipeline
- Advanced thinking stream parsing and token extraction
- Health and model connectivity
"""

import os
import sys
import unittest
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from web_assistant.backend import clean_text_for_speech, get_installed_macos_voices
from web_assistant.web_searcher import search_duckduckgo, fetch_page_text, perform_grounded_web_research


class TestVoiceWebThink(unittest.TestCase):

    def test_clean_text_for_speech_strips_think(self):
        raw = "<think>\nLet us analyze the parity...\nInductive step.\n</think>\n\nThe sum of the numbers is even."
        cleaned = clean_text_for_speech(raw)
        self.assertEqual(cleaned, "The sum of the numbers is even.")

    def test_clean_text_for_speech_strips_code_blocks(self):
        raw = "Here is the code:\n```python\ndef solve(): return 42\n```\nIt works in O(1) time."
        cleaned = clean_text_for_speech(raw)
        self.assertNotIn("def solve()", cleaned)
        self.assertIn("Code block omitted for audio summary.", cleaned)
        self.assertIn("It works in O(1) time.", cleaned)

    def test_clean_text_for_speech_strips_markdown_formatting(self):
        raw = "### Theorem 1\nThis is **strictly** *verified* with `O(n log n)` complexity. See [Source 1](https://example.com)."
        cleaned = clean_text_for_speech(raw)
        self.assertNotIn("###", cleaned)
        self.assertNotIn("**", cleaned)
        self.assertNotIn("`", cleaned)
        self.assertIn("Theorem 1", cleaned)
        self.assertIn("Source 1", cleaned)

    def test_macos_voices_detection(self):
        voices = get_installed_macos_voices()
        self.assertIsInstance(voices, list)
        self.assertGreater(len(voices), 0)
        voice_names = [v["name"] for v in voices]
        self.assertTrue(any("Samantha" in n or "Alex" in n or "Daniel" in n for n in voice_names))

    def test_duckduckgo_search(self):
        hits = search_duckduckgo("Python programming language", max_results=2)
        self.assertIsInstance(hits, list)
        self.assertGreater(len(hits), 0)
        first_hit = hits[0]
        self.assertIn("title", first_hit)
        self.assertIn("href", first_hit)
        self.assertTrue(first_hit["href"].startswith("http"))

    def test_perform_grounded_web_research(self):
        res = perform_grounded_web_research("Apple Silicon M4 Max", max_pages=1)
        self.assertIn("query", res)
        self.assertIn("sources", res)
        self.assertIn("context_text", res)
        self.assertIsInstance(res["sources"], list)
        if res["sources"]:
            self.assertTrue(len(res["context_text"]) > 0)


if __name__ == "__main__":
    unittest.main()
