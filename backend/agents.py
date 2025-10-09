from crewai import Agent, LLM
import os

class ItineraAgents:
    def __init__(self, model="gemini/gemini-2.5-flash", api_key=None):
        self.model = model
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        
        self.llm = LLM(
            model=model, 
            temperature=0.6,
            api_key=self.api_key
        )

        self.prompt_parser_agent = self._create_prompt_parser_agent()
        self.city_selector_agent = self._create_city_selector_agent()
        self.transport_agent = self._create_transport_agent()
        self.local_expert_agent = self._create_local_expert_agent()
        self.budget_manager_agent = self._create_budget_manager_agent()
        self.budget_checker_agent = self._create_budget_checker_agent()
        self.itinerary_agent = self._create_itinerary_agent()

    def _create_prompt_parser_agent(self):
        return Agent(
            role='Travel Request Parser',
            goal='Extract structured travel parameters from natural language requests',
            backstory=(
                "An expert at understanding natural language travel requests. "
                "Skilled at identifying key information like budget, duration, interests, and constraints from conversational input. "
                "Known for asking clarifying questions when information is ambiguous or missing."
            ),
            llm=self.llm,
            verbose=False
        )

    def _create_city_selector_agent(self):
        return Agent(
            role='City Selection Expert',
            goal='Identify affordable and realistic destinations based on constraints',
            backstory=(
                "A budget-conscious travel consultant with expertise in affordable destinations and cost estimation. "
                "Expert at analyzing budgets and determining feasible destinations based on distance, accommodation costs, and local prices."
            ),
            llm=self.llm,
            verbose=False
        )

    def _create_transport_agent(self):
        return Agent(
            role='Transportation Specialist',
            goal='Determine cost-effective and efficient transportation options',
            backstory=(
                "A logistics expert specializing in travel transportation. "
                "Skilled at evaluating flights, trains, buses, and car rentals to optimize travel time and costs."
            ),
            llm=self.llm,
            verbose=False
        )

    def _create_local_expert_agent(self):
        return Agent(
            role='Local Experience Consultant',
            goal='Recommend affordable and enriching local activities',
            backstory=(
                "A travel enthusiast with extensive knowledge of local cultures, attractions, and activities. "
                "Expert at curating budget-friendly experiences that provide authentic insights."
            ),
            llm=self.llm,
            verbose=False
        )

    def _create_budget_manager_agent(self):
        return Agent(
            role='Budget Manager',
            goal='Ensure trip components stay within budget while maximizing value',
            backstory=(
                "A financial planner specializing in travel budgets. "
                "Skilled at allocating funds across transportation, accommodation, food, and activities."
            ),
            llm=self.llm,
            verbose=False
        )

    def _create_budget_checker_agent(self):
        return Agent(
            role='Budget Compliance Checker',
            goal='Validate that plans adhere to budget constraints',
            backstory=(
                "A meticulous budget compliance officer. "
                "Expert at scrutinizing travel plans to ensure expenses align with allocated budget."
            ),
            llm=self.llm,
            verbose=False
        )

    def _create_itinerary_agent(self):
        return Agent(
            role='Itinerary Planner',
            goal='Create detailed and cohesive travel itineraries',
            backstory=(
                "An experienced itinerary planner with talent for organizing complex travel plans. "
                "Skilled at coordinating transportation, accommodation, activities, and downtime into seamless schedules."
            ),
            llm=self.llm,
            verbose=False
        )