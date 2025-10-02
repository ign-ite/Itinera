from flow import TravelPlannerFlow
from dotenv import load_dotenv
import json

def test_travel_plan(test_name, inputs):
    """Test a travel plan configuration"""
    print("\n" + "="*80)
    print(f"TEST: {test_name}")
    print("="*80)
    print(f"Inputs: {json.dumps(inputs, indent=2)}")
    print()
    
    flow = TravelPlannerFlow()
    
    try:
        result = flow.run(inputs)
        flow.save_plan(result, f"plans/travel_plan_{test_name.lower().replace(' ', '_')}.json")
        
        print(f"\n📊 RESULTS:")
        print(f"   Destination: {result['destination']['city']}")
        print(f"   Total Cost: {result['budget']['total_cost']} {inputs['currency']}")
        print(f"   Budget Limit: {inputs['budget']} {inputs['currency']}")
        print(f"   Budget Status: {'✅ Within budget' if result['budget']['within_budget'] else '⚠️ Over budget'}")
        print(f"   Attempts: {result['metadata']['attempts']}")
        
        if not result['budget']['realistic']:
            print(f"\n⚠️ Realism Issues:")
            for issue in result['budget']['validation_issues']:
                print(f"   - {issue}")
        
        return True
        
    except ValueError as e:
        print(f"\n❌ VALIDATION ERROR (Expected): {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    load_dotenv()
    
    tests = [
        {
            "name": "Impossible Budget",
            "inputs": {
                "interests": "luxury hotels, fine dining, shopping",
                "budget": 500,
                "duration": 4,
                "start_city": "Chennai",
                "season": "winter",
                "people": 2,
                "currency": "INR"
            },
            "should_fail": True
        },
        
        {
            "name": "Tight Budget",
            "inputs": {
                "interests": "nature, hiking, local food",
                "budget": 15000,
                "duration": 3,
                "start_city": "Bangalore",
                "season": "monsoon",
                "people": 1,
                "currency": "INR"
            },
            "should_fail": False
        },
        
        {
            "name": "Comfortable Budget",
            "inputs": {
                "interests": "culture, food, history",
                "budget": 50000,
                "duration": 5,
                "start_city": "Mumbai",
                "season": "winter",
                "people": 2,
                "currency": "INR"
            },
            "should_fail": False
        },
        
        {
            "name": "Premium Trip",
            "inputs": {
                "interests": "beaches, adventure, nightlife",
                "budget": 100000,
                "duration": 7,
                "start_city": "Delhi",
                "season": "summer",
                "people": 4,
                "currency": "INR"
            },
            "should_fail": False
        },
        
        {
            "name": "Spiritual Solo",
            "inputs": {
                "interests": "temples, meditation, spirituality",
                "budget": 30000,
                "duration": 4,
                "start_city": "Chennai",
                "season": "winter",
                "people": 1,
                "currency": "INR"
            },
            "should_fail": False
        }
    ]
    
    print("\n" + "🧪"*40)
    print("STARTING TEST SUITE")
    print("🧪"*40)
    
    results = []
    for test in tests:
        success = test_travel_plan(test["name"], test["inputs"])
        
        expected_result = "FAIL" if test["should_fail"] else "PASS"
        actual_result = "FAIL" if not success else "PASS"
        
        test_passed = (expected_result == actual_result)
        
        results.append({
            "name": test["name"],
            "expected": expected_result,
            "actual": actual_result,
            "passed": test_passed
        })
        
        print(f"\nTest Outcome: {'✅ PASS' if test_passed else '❌ FAIL'}")
        print("-"*80)
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for result in results:
        status = "✅" if result["passed"] else "❌"
        print(f"{status} {result['name']}: Expected {result['expected']}, Got {result['actual']}")
    
    total_passed = sum(1 for r in results if r["passed"])
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    
    if total_passed == len(results):
        print("\n All tests passed! System is ready.")
    else:
        print("\n Some tests failed. Review the output above.")