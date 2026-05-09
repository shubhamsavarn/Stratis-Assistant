import requests
import json
import time

BASE_URL = "http://localhost:8000/chat"

test_queries = [
    "Which movie titles performed best in terms of revenue?",
    "What are the key audience behavior trends for 'Stellar Run'?",
    "How does marketing spend correlate with viewership in the European region?",
    "Summarize the content roadmap for the next quarter.",
    "What are the data privacy policy guidelines?",
    "Compare the performance of 'Dark Orbit' vs 'Neo Seoul'."
]

def run_tests():
    print("Starting Final End-to-End Validation...\n")
    for q in test_queries:
        print(f"Testing Query: {q}")
        try:
            start = time.time()
            res = requests.post(BASE_URL, json={"query": q}, timeout=120)
            elapsed = time.time() - start
            if res.status_code == 200:
                data = res.json()
                print(f"Status: SUCCESS ({elapsed:.2f}s)")
                print(f"Thought: {data['thought_trace']}")
                print(f"Answer: {data['answer'][:200]}...")
            else:
                print(f"Status: FAILED ({res.status_code})")
        except Exception as e:
            print(f"Error: {str(e)}")
        print("-" * 50)

if __name__ == "__main__":
    run_tests()
