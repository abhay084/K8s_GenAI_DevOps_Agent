import os
import builtins
import io
import pytest

from k8s_agent import load_env


def test_load_env_sets_missing_keys_only(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("""
GROQ_API_KEY=test-key
OPENAI_BASE_URL=https://example.com/api
MODEL=test-model
""".strip(), encoding="utf-8")

    # Ensure keys are not set before calling
    for key in ["GROQ_API_KEY", "OPENAI_BASE_URL", "MODEL"]:
        monkeypatch.delenv(key, raising=False)

    load_env(str(env_file))

    assert os.getenv("GROQ_API_KEY") == "test-key"
    assert os.getenv("OPENAI_BASE_URL") == "https://example.com/api"
    assert os.getenv("MODEL") == "test-model"


def test_load_env_does_not_override_existing(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("GROQ_API_KEY=new-key", encoding="utf-8")

    monkeypatch.setenv("GROQ_API_KEY", "existing-key")

    load_env(str(env_file))

    # Should keep existing
    assert os.getenv("GROQ_API_KEY") == "existing-key"
