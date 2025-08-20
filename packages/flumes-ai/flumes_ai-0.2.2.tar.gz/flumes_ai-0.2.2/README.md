# Flumes AI – Python SDK
![PyPI](https://img.shields.io/pypi/v/flumes-ai?logo=pypi) ![License](https://img.shields.io/github/license/alex-n-a/flumes-ai-sdk) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alex-n-a/flumes-ai-sdk/blob/main/learning/agent_memory_tutorial_flumes-ai.ipynb)

Flumes AI is a **unified memory infrastructure** for LLM-powered agents and applications. This SDK lets any Python or LangChain stack plug into the [Flumes Memory API](https://docs.flumes.ai/) in **three lines of code**.

👉 Learn more at <https://www.flumes.ai/> – full docs at <https://docs.flumes.ai/>.

---

## 🚀 Installation

```bash
pip install flumes-ai  # includes the OpenAI client by default
```

Python ≥3.8.  No system packages or C-extensions required.

---

## 🔑 Configuration

Environment variables (preferred):

| Service | Variable | Example |
|---------|----------|---------|
| **Flumes** | `FLUMES_API_KEY` | `export FLUMES_API_KEY=sk_live_…` |
| **OpenAI** | `OPENAI_API_KEY` | `export OPENAI_API_KEY=sk-…` |

You can also pass `api_key="…"` directly to `MemoryClient`.

---

## ⚡ Quick-start (entity-first; no summarize route)

```python
from flumes import MemoryClient

client = MemoryClient(api_key="YOUR_KEY", agent_id="travel-bot")
u = client.for_entity("user_001", namespace="prod")

res = u.add("Planning a trip to France. Like wine, cheese and calm places.")
print(res.get("context", {}).get("summary"))

hits = u.search("trip recommendations", top_k=24)
print(len(hits.get("matches", [])))
```

Behind the scenes Flumes:
1. Adds the fact to long-term memory (summarised + deduplicated).
2. Retrieves relevant memories with semantic search.
3. Injects them into the LLM prompt (OpenAI by default).
4. Stores the assistant response for future context.

---

## 🛠️ Advanced (thin pass-through)

```python
from flumes import MemoryClient

mc = MemoryClient(api_key="YOUR_KEY")
mc.search("wine", entity_id="user_42")
mc.get_all(entity_id="user_42", limit=50)
```

All endpoints map 1-to-1 with the [REST reference](https://docs.flumes.ai/api-reference/).

---

## ✨ Key features

* **Semantic search** & vector similarity out-of-the-box.
* **Automatic summarisation & deduplication** (`infer=True` by default).
* **Pluggable LLM backend** – OpenAI today, Claude/Mistral coming.
* **Structured logging** – JSON events (`memory.add.request`, `llm.called`) for easy observability.
* **Timeout & retry helpers** – avoid first-call latency issues.

---

## 🗺 Roadmap

* Async transport with `httpx.AsyncClient`
* CLI: `flumes chat`, `flumes memories list`
* Policy plug-ins: custom summariser / retention strategies
* Local in-process transport (`flumes-core`) for offline testing

---

## 🤝 Contributing

1. Fork the repo and create a feature branch.
2. `make install && make test`
3. Open a PR – we ❤️ community help!

Please see [`LICENSE`](LICENSE) (MIT).

---

Made with 🧠 by the Flumes team – join us on the journey to give every agent a memory!
