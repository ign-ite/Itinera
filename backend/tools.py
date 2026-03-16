import os
import requests


def fetch_travel_prices(start_city: str, destination_city: str) -> str:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "No price data available (TAVILY_API_KEY missing)."

    queries = [
        f"train fare {start_city} to {destination_city} sleeper 3AC price 2025",
        f"budget hotel {destination_city} per night price INR 2025",
        f"restaurant meal cost {destination_city} INR 2025",
    ]

    results = []
    for query in queries:
        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "basic",
                    "include_answer": True,
                    "max_results": 3,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            answer = data.get("answer", "")
            snippets = " | ".join(
                r.get("content", "")[:200]
                for r in data.get("results", [])[:2]
            )
            results.append(f"{query}:\n  Answer: {answer}\n  Details: {snippets}")
        except Exception as e:
            results.append(f"{query}: Could not fetch ({e})")

    return "\n\n".join(results)