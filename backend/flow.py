from crewai import Crew, Process
from agents import ItineraAgents
from tasks import ItineraTasks
import json
import os
from datetime import datetime


class TravelPlannerFlow:
    def __init__(self, model="gemini-2.5-pro", api_key=None):
        """Initialize the travel planner flow with agents and tasks."""
        self.agents = ItineraAgents(model=model, api_key=api_key)
        self.tasks = ItineraTasks()
        
    def validate_inputs(self, inputs):
        """Validate required input parameters."""
        required_fields = ['interests', 'budget', 'duration', 'start_city', 'season', 'people']
        missing = [field for field in required_fields if field not in inputs]
        
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        
        if inputs['budget'] <= 0:
            raise ValueError("Budget must be greater than 0")
        
        if inputs['duration'] <= 0:
            raise ValueError("Duration must be at least 1 day")
        
        if inputs['people'] <= 0:
            raise ValueError("Number of people must be at least 1")
        
        return True
    
    def run(self, inputs):
        """
        Execute the complete travel planning workflow.
        
        Args:
            inputs (dict): Dictionary containing:
                - interests: str (e.g., "culture, food, nature")
                - budget: int/float (total budget)
                - duration: int (number of days)
                - start_city: str (departure city)
                - season: str (e.g., "summer", "winter")
                - people: int (number of travelers)
                - currency: str (optional, default "INR")
        
        Returns:
            dict: Complete travel plan with itinerary, budget, and recommendations
        """
        # Validate inputs
        self.validate_inputs(inputs)
        
        # Add default currency if not provided
        if 'currency' not in inputs:
            inputs['currency'] = 'INR'
        
        print("🌍 Starting travel planning workflow...")
        print(f"📍 Planning trip from {inputs['start_city']}")
        print(f"💰 Budget: {inputs['budget']} {inputs['currency']}")
        print(f"📅 Duration: {inputs['duration']} days")
        print(f"👥 Travelers: {inputs['people']}")
        print("-" * 60)
        
        # Step 1: Choose destination city
        print("\n🎯 Step 1: Selecting optimal destination...")
        city_task = self.tasks.choose_city_task(
            agent=self.agents.city_selector_agent,
            inputs=inputs
        )
        
        city_crew = Crew(
            agents=[self.agents.city_selector_agent],
            tasks=[city_task],
            process=Process.sequential,
            verbose=False
        )
        
        city_result = city_crew.kickoff()
        city_data = self._parse_result(city_result)
        destination_city = city_data.get('destination_city', 'Unknown')
        
        print(f"✅ Destination selected: {destination_city}")
        print(f"💡 Reasoning: {city_data.get('reasoning', 'N/A')}")
        
        # Update inputs with chosen destination
        inputs['destination_city'] = destination_city
        
        # Step 2: Research the city
        print(f"\n🔍 Step 2: Researching {destination_city}...")
        research_task = self.tasks.research_city_task(
            agent=self.agents.local_expert_agent,
            city=destination_city,
            season=inputs['season']
        )
        
        research_crew = Crew(
            agents=[self.agents.local_expert_agent],
            tasks=[research_task],
            process=Process.sequential,
            verbose=False
        )
        
        research_result = research_crew.kickoff()
        city_info = self._parse_result(research_result)
        print(f"✅ Research complete: Found {len(city_info.get('attractions', []))} attractions")
        
        # Step 3: Plan transportation
        print(f"\n🚗 Step 3: Planning transportation...")
        transport_task = self.tasks.transport_task(
            agent=self.agents.transport_agent,
            inputs=inputs,
            city=destination_city
        )
        
        transport_crew = Crew(
            agents=[self.agents.transport_agent],
            tasks=[transport_task],
            process=Process.sequential,
            verbose=False
        )
        
        transport_result = transport_crew.kickoff()
        transport_info = self._parse_result(transport_result)
        print("✅ Transportation options identified")
        
        # Step 4: Create itinerary
        print(f"\n📋 Step 4: Creating {inputs['duration']}-day itinerary...")
        itinerary_task = self.tasks.itinerary_planning_task(
            agent=self.agents.itinerary_agent,
            inputs=inputs,
            city_info=city_info
        )
        
        itinerary_crew = Crew(
            agents=[self.agents.itinerary_agent],
            tasks=[itinerary_task],
            process=Process.sequential,
            verbose=False
        )
        
        itinerary_result = itinerary_crew.kickoff()
        itinerary_data = self._parse_result(itinerary_result)
        print(f"✅ Itinerary created with {len(itinerary_data.get('itinerary', []))} days planned")
        
        # Step 5: Plan budget
        print(f"\n💵 Step 5: Creating detailed budget...")
        budget_task = self.tasks.budget_planning_task(
            agent=self.agents.budget_manager_agent,
            inputs=inputs,
            itinerary=itinerary_data,
            city=destination_city
        )
        
        budget_crew = Crew(
            agents=[self.agents.budget_manager_agent],
            tasks=[budget_task],
            process=Process.sequential,
            verbose=False
        )
        
        budget_result = budget_crew.kickoff()
        budget_data = self._parse_result(budget_result)
        print(f"✅ Budget planned: {budget_data.get('total_estimated_cost', 0)} {inputs['currency']}")
        
        # Step 6: Validate budget
        print(f"\n✔️  Step 6: Validating budget compliance...")
        budget_check_task = self.tasks.budget_check_task(
            agent=self.agents.budget_checker_agent,
            inputs=inputs,
            budget_plan=budget_data,
            city=destination_city
        )
        
        budget_check_crew = Crew(
            agents=[self.agents.budget_checker_agent],
            tasks=[budget_check_task],
            process=Process.sequential,
            verbose=False
        )
        
        budget_check_result = budget_check_crew.kickoff()
        budget_validation = self._parse_result(budget_check_result)
        
        within_budget = budget_validation.get('within_budget', False)
        status = "✅ Within budget" if within_budget else "⚠️  Over budget"
        print(f"{status}: {budget_validation.get('computed_total', 0)} {inputs['currency']}")
        
        # Step 7: Compile final plan
        print("\n📦 Step 7: Compiling final travel plan...")
        
        final_plan = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "trip_duration": inputs['duration'],
                "travelers": inputs['people'],
                "currency": inputs['currency'],
                "start_city": inputs['start_city']
            },
            "destination": {
                "city": destination_city,
                "selection_reasoning": city_data.get('reasoning', ''),
                "research": city_info
            },
            "transportation": transport_info,
            "itinerary": itinerary_data,
            "budget": {
                "plan": budget_data,
                "validation": budget_validation,
                "total_cost": budget_validation.get('computed_total', budget_data.get('total_estimated_cost', 0)),
                "within_budget": within_budget,
                "budget_limit": inputs['budget']
            },
            "recommendations": budget_validation.get('recommendations', [])
        }
        
        print("\n" + "=" * 60)
        print("🎉 Travel planning complete!")
        print("=" * 60)
        
        return final_plan
    
    def _parse_result(self, result):
        """Parse CrewAI result and extract JSON data."""
        try:
            # Handle different result types
            if hasattr(result, 'raw'):
                result_str = result.raw
            elif hasattr(result, 'output'):
                result_str = result.output
            else:
                result_str = str(result)
            
            # Try to extract JSON from markdown code blocks
            if '```json' in result_str:
                json_str = result_str.split('```json')[1].split('```')[0].strip()
            elif '```' in result_str:
                json_str = result_str.split('```')[1].split('```')[0].strip()
            else:
                json_str = result_str
            
            # Parse JSON
            return json.loads(json_str)
        except (json.JSONDecodeError, IndexError, AttributeError) as e:
            print(f"⚠️  Warning: Could not parse result as JSON: {e}")
            return {"raw_output": str(result)}
    
    def save_plan(self, plan, filename="travel_plan.json"):
        """Save the travel plan to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Travel plan saved to {filename}")


# Example usage
if __name__ == "__main__":
    # Sample inputs
    travel_inputs = {
        "interests": "culture, food, history",
        "budget": 50000,
        "duration": 5,
        "start_city": "Mumbai",
        "season": "winter",
        "people": 2,
        "currency": "INR"
    }
    
    # Initialize and run flow
    flow = TravelPlannerFlow()
    
    try:
        result = flow.run(travel_inputs)
        
        # Save the plan
        flow.save_plan(result)
        
        # Print summary
        print(f"\n📊 Summary:")
        print(f"   Destination: {result['destination']['city']}")
        print(f"   Total Cost: {result['budget']['total_cost']} {travel_inputs['currency']}")
        print(f"   Budget Status: {'✅ Within budget' if result['budget']['within_budget'] else '⚠️  Over budget'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()