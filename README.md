# Kubernetes GenAI Agent

A minimal GenAI agent for Kubernetes operations using an OpenAI-compatible API (via Groq).

## Architecture Diagram

![Architecture Diagram](Mermaid%20Chart-2025-08-24-094404.png)

## Setup

1) Install deps
```bash
pip install -r requirements.txt
```

2) Configure environment
```bash
cp .env.example .env
# edit .env to set GROQ_API_KEY (and optionally OPENAI_BASE_URL, MODEL)
```

## Run (CLI)

```bash
python k8s_agent.py
```

## More docs

See advanced usage, configuration, and troubleshooting in `docs/ADVANCED.md`.

## License

This project is open source. See LICENSE file for details.
