import os
import sys

# Add current directory to path so 'backend' module is found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.main import app
import uvicorn

if __name__ == "__main__":
    print("Starting Secure AI Insights Assistant Backend...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
