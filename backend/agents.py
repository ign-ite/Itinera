from numpy import number
from crewai import Agent, Task, Crew, LLM
import json
import os 
import sys

class ItineraAgents:
    def __init__(self, model="gemini/gemini-2.5-pro", api_key=None):
        self.model = model
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

        self.llm = LLM(
            model=model, 
            temperature=0.6,
            api_key=self.api_key
        )

        self.city_selector_agent = self._create_city_selector_agent()
        self.transport_agent = self._create_transport_agent()
        self.hotel_agent = self._create_hotel_agent()
        self.local_expert_agent = self._create_local_expert_agent()
        self.budget_manager_agent = self._create_budget_manager_agent()
        self.budget_checker_agent = self._create_budget_checker_agent()
        self.itinerary_agent = self._create_itinerary_agent()

    def _create_city_selector_agent(self):
        return Agent(
            role='City Selection and Budget Optimization Expert',
            goal='Identify affordable and realistic destinations based on user budget constraints',
            backstory=(
                "A budget-conscious travel consultant with expertise in affordable destinations and travel cost estimation. "
                "Expert at analyzing travel budgets and determining feasible destinations based on distance, accommodation costs, "
                "and local prices. Known for recommending realistic options that maximize experiences while strictly respecting budget constraints."
            ),
            llm=self.llm,
            verbose=False
        )

    def _create_transport_agent(self):
        return Agent(
            role='Transportation and Logistics Specialist',
            goal='Determine the most cost-effective and efficient transportation options for the trip',
            backstory=(
                "A logistics expert specializing in travel transportation. Skilled at evaluating various modes of transport including flights, trains, buses, and car rentals. "
                "Expertise in finding the best deals, routes, and schedules to optimize travel time and costs. Known for balancing convenience with budget considerations to ensure smooth travel experiences."
            ),
            llm=self.llm,
            verbose=False
        )

    def _create_hotel_agent(self):
        return Agent(
            role='Accommodation and Lodging Advisor',
            goal='Find affordable and comfortable lodging options that fit within the budget',
            backstory=(
                "A seasoned travel accommodation specialist with deep knowledge of hotels, hostels, vacation rentals, and alternative lodging options. "
                "Expert at sourcing budget-friendly yet comfortable places to stay, considering factors like location, amenities, and guest reviews. "
                "Known for negotiating deals and finding hidden gems that provide great value without compromising on quality."
            ),
            llm=self.llm,
            verbose=False
        )

    def _create_local_expert_agent(self):
        return Agent(
            role='Local Experience and Activity Consultant',
            goal='Recommend affordable and enriching local activities and experiences',
            backstory=(
                "A travel enthusiast with extensive knowledge of local cultures, attractions, and activities. "
                "Expert at curating unique and budget-friendly experiences that allow travelers to immerse themselves in the local way of life. "
                "Known for uncovering off-the-beaten-path activities, free events, and cultural experiences that provide authentic insights without breaking the bank."
            ),
            llm=self.llm,
            verbose=False
        )

    def _create_budget_manager_agent(self):
        return Agent(
            role='Budget Management and Financial Planner',
            goal='Ensure all trip components stay within the overall budget while maximizing value',
            backstory=(
                "A financial planner specializing in travel budgets. Skilled at allocating funds across various trip components including transportation, accommodation, food, and activities. "
                "Expertise in cost estimation, expense tracking, and budget optimization to ensure travelers get the most out of their money. "
                "Known for creative budgeting strategies that allow for memorable experiences without overspending."
            ),
            llm=self.llm,
            verbose=False
        )

    def _create_budget_checker_agent(self):
        return Agent(
            role='Budget Compliance Checker',
            goal='Review and validate that all trip plans adhere to the specified budget constraints',
            backstory=(
                "A meticulous budget compliance officer with a keen eye for detail. "
                "Expert at scrutinizing travel plans to ensure every expense aligns with the allocated budget. "
                "Known for identifying potential oversights and suggesting adjustments to keep the trip financially on track while still delivering a fulfilling experience."
            ),
            llm=self.llm,
            verbose=False
        )

    def _create_itinerary_agent(self):
        return Agent(
            role='Itinerary Planner and Coordinator',
            goal='Create a detailed and cohesive travel itinerary that integrates all trip components',
            backstory=(
                "An experienced itinerary planner with a talent for organizing complex travel plans. "
                "Skilled at coordinating transportation, accommodation, activities, and downtime into a seamless schedule. "
                "Known for balancing structure with flexibility to ensure travelers have a well-paced and enjoyable experience."
            ),
            llm=self.llm,
            verbose=False
        )