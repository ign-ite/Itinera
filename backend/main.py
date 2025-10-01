from flow import TravelPlannerFlow
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    
    travel_inputs = {
        "interests": "culture, food, history",
        "budget": 50000,
        "duration": 5,
        "start_city": "Mumbai",
        "season": "winter",
        "people": 2,
        "currency": "INR"
    }
    
    flow = TravelPlannerFlow()
    
    try:
        result = flow.run(travel_inputs)
        
        flow.save_plan(result)
        
        print(f"\n📊 Summary:")
        print(f"   Destination: {result['destination']['city']}")
        print(f"   Total Cost: {result['budget']['total_cost']} {travel_inputs['currency']}")
        print(f"   Budget Status: {'✅ Within budget' if result['budget']['within_budget'] else '⚠️  Over budget'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
