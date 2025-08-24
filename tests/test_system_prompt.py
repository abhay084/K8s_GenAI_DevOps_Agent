import os
from k8s_agent import load_system_prompt, DEFAULT_SYSTEM_PROMPT


def test_system_prompt_env_precedence(monkeypatch, tmp_path):
    # Even if TOML has a value, env should take precedence
    toml_path = tmp_path / "system_promtp.toml"
    toml_path.write_text('system_prompt = """From TOML"""', encoding="utf-8")

    monkeypatch.setenv("SYSTEM_PROMPT", "From ENV")
    prompt = load_system_prompt(str(toml_path))
    assert prompt == "From ENV"


def test_system_prompt_from_toml_when_no_env(monkeypatch, tmp_path):
    toml_path = tmp_path / "system_promtp.toml"
    toml_path.write_text('system_prompt = """From TOML"""', encoding="utf-8")

    monkeypatch.delenv("SYSTEM_PROMPT", raising=False)
    prompt = load_system_prompt(str(toml_path))
    assert prompt == "From TOML"


def test_system_prompt_default_when_missing(monkeypatch, tmp_path):
    monkeypatch.delenv("SYSTEM_PROMPT", raising=False)
    prompt = load_system_prompt(str(tmp_path / "missing.toml"))
    assert prompt == DEFAULT_SYSTEM_PROMPT
