import os
import sys
from backend.core.agent_engine import get_agent_executor

# Ensure the parent directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

test_queries = [
    "Which titles performed best in 2025?",
    "Why is Stellar Run trending recently?",
    "Compare Dark Orbit vs Last Kingdom.",
    "Which city had the strongest engagement last month?",
    "What explains weak comedy performance?",
    "What recommendations would you give for leadership?"
]

def check_ai():
    print("Initializing Agent...")
    agent = get_agent_executor()
    
    for i, q in enumerate(test_queries, 1):
        print(f"\n[{i}/6] Testing Query: {q}")
        print("-" * 30)
        try:
            result = agent.invoke(q)
            print(f"THOUGHT: {result.get('thought')}")
            print(f"RESPONSE: {result.get('output')}")
            if result.get('data'):
                print(f"DATA RETURNED: Yes ({len(result['data'])} rows)")
            else:
                print("DATA RETURNED: No")
        except Exception as e:
            print(f"ERROR: {str(e)}")
        print("-" * 30)

if __name__ == "__main__":
    check_ai()
