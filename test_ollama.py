from langchain_ollama import ChatOllama

try:
    print("Connecting to Ollama with phi3...")
    llm = ChatOllama(model="phi3")
    response = llm.invoke("Hello, are you working? Please respond with 'YES' if you are.")
    print("Response from Ollama:")
    print(response.content)
except Exception as e:
    print(f"Error connecting to Ollama: {str(e)}")
