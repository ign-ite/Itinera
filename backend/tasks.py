from crewai import Task
import json

class ItineraTasks:
    def __init__(self):
        pass

    def _make_task(self, description: str, agent, expected_output: str, context=None):
        task_params = {
            'description': description.strip(),
            'expected_output': expected_output.strip(),
            'agent': agent
        }
        
        if context:
            task_params['context'] = context
            
        return Task(**task_params)

    def parse_prompt_task(self, agent, prompt):
        description = f"""
        Parse this natural language travel request and extract structured information:
        
        "{prompt}"
        
        Extract:
        - Budget: Total amount in INR (if not specified, ask user or estimate based on trip type)
        - Duration: Number of days
        - Start city: Departure location
        - Interests: Activities, experiences, or trip type (e.g., adventure, culture, relaxation)
        - Season: When they want to travel (current season if not specified)
        - People: Number of travelers (default to 1 if not mentioned)
        
        If critical information is missing, make reasonable assumptions based on context.
        """
        
        expected_output = """
        {
            "budget": number,
            "duration": number,
            "start_city": "string",
            "interests": "string",
            "season": "summer/winter/monsoon/spring/autumn",
            "people": number,
            "currency": "INR",
            "missing_info": ["list of any critical missing information"],
            "assumptions": "string explaining any assumptions made"
        }
        """
        
        return self._make_task(description, agent, expected_output)

    def choose_city_task(self, agent, inputs):
        description = f"""
        Select an affordable and realistic destination based on:
        - Interests: {inputs['interests']}
        - Budget: {inputs['budget']} {inputs.get('currency', 'INR')}
        - Duration: {inputs['duration']} days
        - Start city: {inputs['start_city']}
        - Season: {inputs['season']}
        - People: {inputs['people']}
        
        Consider distance, accommodation costs, and local prices.
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
        Research {city} for {season} travel:
        - Top attractions and landmarks
        - Local food and cuisine highlights
        - Cultural experiences and seasonal events
        - Local customs and etiquette
        - Transportation and safety tips
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
        
        Budget: {inputs['budget']} {inputs.get('currency', 'INR')}
        Interests: {inputs['interests']}
        Season: {inputs['season']}
        
        City Information:
        {json.dumps(city_info, indent=2)}
        
        Include day-by-day activities, sightseeing, transportation, and meal recommendations.
        """
        
        expected_output = """
        {
            "itinerary": [
                {
                    "day": number,
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
        Create detailed budget for {inputs['duration']}-day trip for {inputs['people']} people 
        from {inputs['start_city']} to {city}.
        Max budget: {inputs['budget']} {inputs.get('currency', 'INR')}.

        Calculate with itemized breakdown:

        1. TRANSPORTATION:
           - Round trip: [mode] × {inputs['people']} = X INR
           - Local transport: Y INR × {inputs['duration']} days = Z INR

        2. ACCOMMODATION:
           - Per night: A INR × {inputs['duration']} nights = B INR

        3. MEALS:
           - Breakfast: {inputs['people']} × {inputs['duration']} × 150 = X INR
           - Lunch: {inputs['people']} × {inputs['duration']} × 250 = Y INR
           - Dinner: {inputs['people']} × {inputs['duration']} × 300 = Z INR

        4. ACTIVITIES: [List each with cost × {inputs['people']}]

        5. EMERGENCY FUND: 10% of total

        6. VISA FEES: 0 INR (domestic)

        Use CURRENT realistic prices. Show calculations. If over budget, suggest cost-cutting measures.
        """
        
        expected_output = """
        {
            "transportation": [{"description": "string", "cost": number, "calculation": "string"}],
            "accommodation": [{"description": "string", "cost": number, "calculation": "string"}],
            "meals": [{"type": "string", "cost": number, "calculation": "string"}],
            "activities": [{"name": "string", "cost": number, "calculation": "string"}],
            "emergency_fund": {"description": "string", "cost": number},
            "visa_fees": {"description": "string", "cost": number},
            "total_estimated_cost": number,
            "budget_status": "within/over",
            "cost_cutting_suggestions": ["string"]
        }
        """
        
        return self._make_task(description, agent, expected_output)

    def budget_check_task(self, agent, inputs, budget_plan, city):
        currency = inputs.get("currency", "INR")
        description = f"""
        Verify budget plan for {inputs['duration']}-day trip for {inputs['people']} people 
        from {inputs['start_city']} to {city}.
        Budget limit: {inputs['budget']} {currency}.

        Budget Plan:
        {json.dumps(budget_plan, indent=2)}

        Check all categories and return corrected totals if discrepancies found.
        """
        
        expected_output = f"""
        {{
            "currency": "{currency}",
            "verified_at": "ISO8601 timestamp",
            "categories": {{
                "accommodation": [...],
                "transportation": [...],
                "activities": [...],
                "meals": [...],
                "emergency_fund": {{}},
                "visa_fees": {{}}
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
        Recommend transportation options from {inputs['start_city']} to {city}.
        
        Evaluate cost, convenience, and travel time for:
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