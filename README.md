# Itinera

Multi-agent travel planner built with CrewAI and the Gemini API.

You describe a trip (interests, budget, duration, start city, season, group size). A set of specialist agents breaks the request into parts and pulls data from external APIs, and the backend validates the plan against your budget before returning it.

## Stack

- Backend: Python, CrewAI, FastAPI, Pydantic, Gemini (via `langchain-google-genai`)
- Frontend: React and Tailwind CSS (`frontend/`)
- Sample generated plans: `generated_plans/`

## Run it locally

1. Clone the repo and install the backend dependencies:
   ```bash
   pip install -r req.txt
   ```
2. Create a `.env` file with your keys:
   ```
   GEMINI_API_KEY=your_key_here
   GOOGLE_API_KEY=your_key_here
   TAVILY_API_KEY=optional_price_search_key
   ```
3. Start the API from the `backend/` folder:
   ```bash
   uvicorn api:app --reload
   ```
4. Start the frontend from the `frontend/` folder:
   ```bash
   npm install
   npm start
   ```

## Status

Prototype. Orchestration is CrewAI; an earlier version of this project used a different framework.
