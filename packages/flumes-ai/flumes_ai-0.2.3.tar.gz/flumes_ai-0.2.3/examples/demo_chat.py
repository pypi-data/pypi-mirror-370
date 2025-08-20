import os, sys

from flumes import MemoryClient, Agent


def main():
    """End-to-end demo talking to the live Flumes API."""

    api_key = os.getenv("FLUMES_API_KEY")
    if not api_key:
        sys.stderr.write("\n⚠️  Please `export FLUMES_API_KEY=sk_...` before running this script.\n")
        sys.exit(1)

    # --------------- Low-level CRUD -----------------
    agent_id = "demo_travel_bot"
    entity_id = "user_001"
    mc = MemoryClient(api_key=api_key, agent_id=agent_id)

    print("Health:", mc.health())
    print("Meta:", mc.meta())

    print("Adding a memory …")
    mc.add(
        input="Planning a trip to France. Like wine, cheese and calm places.",
        entity_id=entity_id,
        namespace="prod",
        budget="standard",
    )

    print("Searching memories …")
    hits = mc.search("trip recommendations", entity_id=entity_id, namespace="prod", top_k=24)
    print("Search matches:", len(hits.get("matches", [])))

    # --------------- High-level Agent chat ---------
    # Requires OPENAI_API_KEY (or uses env var if already set)
    agent = Agent(agent_id=agent_id, entity_id=entity_id)

    print("Storing agent memory …")
    agent.remember("I prefer museums over nightlife.")

    print("Asking agent …")
    reply = agent.chat("Can you suggest a 3-day itinerary in France?")
    print("Agent replied:", reply)


if __name__ == "__main__":
    main()
