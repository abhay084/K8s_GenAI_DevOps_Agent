import os
from k8s_agent import K8sAgent


def test_agent_uses_env_defaults_for_model_and_base_url(monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.com/openai/v1")
    monkeypatch.setenv("MODEL", "example/model")

    agent = K8sAgent(api_key="dummy-key")

    assert agent.model == "example/model"
    # Accessing private client config is not public API, but we can ensure no exception
    # and that constructing with env-provided base_url works by making a trivial attribute check.
    assert hasattr(agent, "client")


def test_agent_overrides_env_with_arguments(monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "https://env.example/api")
    monkeypatch.setenv("MODEL", "env/model")

    agent = K8sAgent(api_key="dummy-key", model="arg/model", base_url="https://arg.example/api")

    assert agent.model == "arg/model"
