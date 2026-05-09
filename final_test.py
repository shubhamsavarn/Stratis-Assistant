import requests
import json
import time

BASE_URL = "http://localhost:8000/chat"

# The 6 Mandatory Business Questions
test_queries = [
    "Which titles performed best in 2025?",
    "Why is Stellar Run trending recently?",
    "Compare Dark Orbit vs Last Kingdom.",
    "Which city had the strongest engagement last month?",
    "What explains weak comedy performance?",
    "What recommendations would you give for leadership?"
]

def run_tests():
    print("Starting Official Business Scenario Validation...\n")
    for q in test_queries:
        print(f"Testing Query: {q}")
        try:
            start = time.time()
            res = requests.post(
                BASE_URL, 
                json={"query": q}, 
                headers={"X-API-KEY": "sk-insight-flow-2025"}, 
                timeout=120
            )
            elapsed = time.time() - start
            if res.status_code == 200:
                data = res.json()
                print(f"Status: SUCCESS ({elapsed:.2f}s)")
                print(f"Agent Logic: {data.get('thought_trace', 'No trace')}")
                print(f"Assistant Answer: {data['answer']}")
            else:
                print(f"Status: FAILED ({res.status_code})")
        except Exception as e:
            print(f"Error: {str(e)}")
        print("-" * 50)

if __name__ == "__main__":
    run_tests()
