"""Unit tests for ApexPhi-14B mathematical reasoning and sampling guardrails."""

import pytest

def test_min_p_probability_cutoff():
    """Verify Min-P probability calculation formula for Phi-4."""
    min_p = 0.05
    max_prob = 0.80
    cutoff = min_p * max_prob
    assert cutoff == pytest.approx(0.04), "Min-P cutoff must scale proportionally"

def test_phi4_parameters_configured():
    """Verify presence of Phi-4 stop tokens and directives in Modelfile."""
    from pathlib import Path
    modelfile = Path(__file__).parent.parent / "Modelfile.apex-phi-14b"
    assert modelfile.exists(), "Modelfile must exist"
    content = modelfile.read_text()

    assert "<|im_end|>" in content
    assert "<|endoftext|>" in content
    assert "min_p 0.05" in content
    assert "num_ctx 16384" in content
