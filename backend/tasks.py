from crewai import Task
import json


class ItineraTasks:
    def __init__(self):
        pass

    def _make_task(self, description: str, agent, expected_output: str, context=None):
        """Helper to reduce boilerplate when defining tasks."""
        # Ensure all parameters are passed as keyword arguments
        task_params = {
            'description': description.strip(),
            'expected_output': expected_output.strip(),
            'agent': agent
        }
        
        if context:
            task_params['context'] = context
            
        return Task(**task_params)

    def choose_city_task(self, agent, inputs):
        description = f"""
        Analyze the user's budget and preferences to select an affordable and realistic travel destination.
        Consider distance, accommodation costs, and local prices.

        - Interests: {inputs['interests']}
        - Budget: {inputs['budget']}
        - Duration: {inputs['duration']} days
        - Start city: {inputs['start_city']}
        - Season: {inputs['season']}
        """
        expected_output = """
        {
            "destination_city": "string",
            "reasoning": "string"
        }
        """
        return self._make_task(description, agent, expected_output)

    def research_city_task(self, agent, city, season):
        description = f"""
        Research {city} with focus on:
        - Top attractions and landmarks
        - Local food and cuisine highlights
        - Cultural experiences and seasonal events
        - Local customs and etiquette
        - Transportation and safety tips
        - Tips for traveling in {season}
        """
        expected_output = """
        {
            "attractions": ["string"],
            "cuisine": ["string"],
            "cultural_norms": ["string"],
            "transportation_tips": ["string"],
            "local_activities": ["string"]
        }
        """
        return self._make_task(description, agent, expected_output)

    def itinerary_planning_task(self, agent, inputs, city_info):
        description = f"""
        Create a {inputs['duration']}-day itinerary for {inputs['destination_city']}.

        Constraints:
        - Budget: {inputs['budget']}
        - Interests: {inputs['interests']}
        - Season: {inputs['season']}

        City Information:
        {json.dumps(city_info)}

        Plan must include:
        - Transportation (to and within city)
        - Accommodation suggestions
        - Day-by-day activities and sightseeing
        - Meal recommendations
        """
        expected_output = """
        {
            "itinerary": [
                {
                    "day": "integer",
                    "activities": [
                        {
                            "activity": "string",
                            "time": "string",
                            "location": "string",
                            "description": "string",
                            "transportation": "string"
                        }
                    ]
                }
            ]
        }
        """
        return self._make_task(description, agent, expected_output)

    def budget_planning_task(self, agent, inputs, itinerary, city):
        description = f"""
        Create a detailed budget for a {inputs['duration']}-day trip
        for {inputs['people']} people from {inputs['start_city']} to {city}.
        Max budget: {inputs['budget']}.

        Include:
        - Transport (round-trip + local)
        - Accommodation
        - Activities (with entry costs)
        - Meals (all days)
        - Emergency fund & visa fees

        Requirements:
        - Use approximate CURRENT prices
        - Provide a clear JSON breakdown
        - Validate total ≤ {inputs['budget']}
        - If over budget, suggest adjustments
        """
        expected_output = """
        {
            "transportation": [...],
            "accommodation": [...],
            "activities": [...],
            "meals": [...],
            "emergency_fund": ...,
            "visa_fees": ...,
            "total_estimated_cost": ...
        }
        """
        return self._make_task(description, agent, expected_output)

    def budget_check_task(self, agent, inputs, budget_plan, city):
        currency = inputs.get("currency", "INR")
        description = f"""
        Verify and validate the budget plan for a {inputs['duration']}-day trip
        for {inputs['people']} people from {inputs['start_city']} to {city}.
        Budget: {inputs['budget']} {currency}.

        Check all categories (accommodation, transport, activities, meals, visa, emergency).
        Return corrected totals if discrepancies found.
        
        Budget Plan to Verify:
        {json.dumps(budget_plan, indent=2)}
        """
        expected_output = f"""
        {{
          "schema_version": "1.0",
          "currency": "{currency}",
          "verified_at": "ISO8601 timestamp",
          "categories": {{
            "accommodation": [...],
            "transportation": [...],
            "activities": [...],
            "meals": [...],
            "emergency_fund": {{...}},
            "visa_fees": {{...}}
          }},
          "computed_total": number,
          "original_total_in_plan": number,
          "discrepancy": number,
          "within_budget": boolean,
          "over_by": number,
          "flags": [...],
          "recommendations": [...]
        }}
        """
        return self._make_task(description, agent, expected_output)

    def transport_task(self, agent, inputs, city):
        description = f"""
        Recommend best transportation options for trip from {inputs['start_city']} to {city}.

        Evaluate:
        - Cost, convenience, travel time
        - Long-distance travel to destination
        - Local transportation within city
        """
        expected_output = """
        {
            "long_distance_options": ["string"],
            "local_transport_options": ["string"],
            "reasoning": "string"
        }
        """
        return self._make_task(description, agent, expected_output)