from crewai import Crew, Process
from agents import ItineraAgents
from tasks import ItineraTasks
import json
import os
from datetime import datetime


class TravelPlannerFlow:
    def __init__(self, model="gemini/gemini-2.0-flash-exp", api_key=None):
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
    
    def validate_feasibility(self, inputs):
        """Quick feasibility check before running full workflow"""
        min_daily_cost_per_person = 1500 
        min_total = inputs['people'] * inputs['duration'] * min_daily_cost_per_person
        
        if inputs['budget'] < min_total:
            return {
                'feasible': False,
                'message': (
                    f"Budget {inputs['budget']} INR is insufficient for {inputs['people']} people "
                    f"for {inputs['duration']} days. Minimum realistic budget: {min_total} INR "
                    f"({min_daily_cost_per_person} INR per person per day)."
                )
            }
        
        max_reasonable = inputs['people'] * inputs['duration'] * 50000 
        if inputs['budget'] > max_reasonable:
            print(f"Warning: Budget {inputs['budget']} INR seems very high. Are you sure?")
        
        return {'feasible': True}
    
    def validate_budget_realistic(self, plan, inputs):
        """Programmatic validation - don't trust LLM math alone"""
        budget_data = plan.get('budget', {}).get('plan', {})
        total = plan.get('budget', {}).get('total_cost', 0)
        
        issues = []
        
        min_per_person_per_day = 1000
        min_expected = inputs['people'] * inputs['duration'] * min_per_person_per_day
        
        if total < min_expected:
            issues.append(
                f"Total cost {total} INR is unrealistically low. "
                f"Minimum expected: {min_expected} INR"
            )
        
        if 'accommodation' in budget_data:
            acc_items = budget_data['accommodation']
            if isinstance(acc_items, list) and len(acc_items) > 0:
                acc_total = sum(item.get('cost', 0) for item in acc_items)
                min_acc = inputs['duration'] * 800  
                if acc_total < min_acc:
                    issues.append(
                        f"Accommodation cost {acc_total} INR is too low. "
                        f"Minimum: {min_acc} INR for {inputs['duration']} nights"
                    )
        
        if 'meals' in budget_data:
            meal_items = budget_data['meals']
            if isinstance(meal_items, list):
                meal_total = sum(item.get('cost', 0) for item in meal_items)
                min_meals = inputs['people'] * inputs['duration'] * 3 * 150  
                if meal_total < min_meals:
                    issues.append(
                        f"Meal cost {meal_total} INR seems low. "
                        f"Expected minimum: {min_meals} INR"
                    )
        
        return {
            'realistic': len(issues) == 0,
            'issues': issues
        }
    
    def run(self, inputs, max_retries=2):
        """
        Execute the complete travel planning workflow with validation and retries.
        
        Args:
            inputs (dict): Dictionary containing trip parameters
            max_retries (int): Number of times to retry if budget fails
        
        Returns:
            dict: Complete travel plan with itinerary, budget, and recommendations
        """
        self.validate_inputs(inputs)
        
        if 'currency' not in inputs:
            inputs['currency'] = 'INR'
        
        feasibility = self.validate_feasibility(inputs)
        if not feasibility['feasible']:
            raise ValueError(feasibility['message'])
        
        print("Starting travel planning workflow...")
        print(f"Planning trip from {inputs['start_city']}")
        print(f"Budget: {inputs['budget']} {inputs['currency']}")
        print(f"Duration: {inputs['duration']} days")
        print(f"Travelers: {inputs['people']}")
        print("-" * 60)
        
        original_budget = inputs['budget']
        
        for attempt in range(max_retries):
            try:
                print(f"\nAttempt {attempt + 1}/{max_retries}")
                
                print(f"\nStep 1: Selecting optimal destination...")
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
                
                print(f"Destination selected: {destination_city}")
                print(f"Reasoning: {city_data.get('reasoning', 'N/A')}")
                
                inputs['destination_city'] = destination_city
                
                print(f"\nStep 2: Researching {destination_city}...")
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
                print(f"Research complete: Found {len(city_info.get('attractions', []))} attractions")
                
                print(f"\nStep 3: Planning transportation...")
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
                print("Transportation options identified")
                
                print(f"\nStep 4: Creating {inputs['duration']}-day itinerary...")
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
                print(f"Itinerary created with {len(itinerary_data.get('itinerary', []))} days planned")
                
                print(f"\nStep 5: Creating detailed budget...")
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
                print(f"Budget planned: {budget_data.get('total_estimated_cost', 0)} {inputs['currency']}")
                
                print(f"\nStep 6: Validating budget compliance...")
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
                computed_total = budget_validation.get('computed_total', budget_data.get('total_estimated_cost', 0))
                
                status = "Within budget" if within_budget else "Over budget"
                print(f"{status}: {computed_total} {inputs['currency']}")
                
                validation_result = self.validate_budget_realistic(
                    {'budget': {'plan': budget_data, 'total_cost': computed_total}},
                    inputs
                )
                
                if not validation_result['realistic']:
                    print("\nWarning: Budget calculations seem unrealistic:")
                    for issue in validation_result['issues']:
                        print(f"  - {issue}")
                
                if not within_budget and attempt < max_retries - 1:
                    print(f"\nPlan exceeds budget. Retrying with stricter constraints...")
                    inputs['budget'] = int(original_budget * 0.85)
                    continue
                
                if not within_budget and attempt == max_retries - 1:
                    raise ValueError(
                        f"Could not generate plan within budget {original_budget} {inputs['currency']} "
                        f"after {max_retries} attempts. Final cost: {computed_total} {inputs['currency']}. "
                        f"Try increasing your budget or reducing trip duration/travelers."
                    )
                
                print("\nStep 7: Compiling final travel plan...")
                
                final_plan = {
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "trip_duration": inputs['duration'],
                        "travelers": inputs['people'],
                        "currency": inputs['currency'],
                        "start_city": inputs['start_city'],
                        "attempts": attempt + 1
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
                        "total_cost": computed_total,
                        "within_budget": within_budget,
                        "budget_limit": original_budget,
                        "realistic": validation_result['realistic'],
                        "validation_issues": validation_result['issues']
                    },
                    "recommendations": budget_validation.get('recommendations', [])
                }
                
                print("\n" + "=" * 60)
                print("Travel planning complete!")
                print("=" * 60)
                
                return final_plan
                
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"\nError occurred: {e}")
                    print("Retrying...")
                    continue
                else:
                    raise
        
        raise ValueError(f"Failed to generate plan after {max_retries} attempts")
    
    def _parse_result(self, result):
        """Parse CrewAI result and extract JSON data."""
        try:
            if hasattr(result, 'raw'):
                result_str = result.raw
            elif hasattr(result, 'output'):
                result_str = result.output
            else:
                result_str = str(result)
            
            if '```json' in result_str:
                json_str = result_str.split('```json')[1].split('```')[0].strip()
            elif '```' in result_str:
                json_str = result_str.split('```')[1].split('```')[0].strip()
            else:
                json_str = result_str
            
            return json.loads(json_str)
        except (json.JSONDecodeError, IndexError, AttributeError) as e:
            print(f"Warning: Could not parse result as JSON: {e}")
            try:
                from json_repair import repair_json
                return json.loads(repair_json(json_str))
            except:
                return {"raw_output": str(result)}
    
    def save_plan(self, plan, filename="travel_plan.json"):
        """Save the travel plan to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        print(f"\nTravel plan saved to {filename}")