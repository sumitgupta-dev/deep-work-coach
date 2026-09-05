import requests

# Your local Ollama server address
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3.2:1b"

def ask_ai(prompt: str):
    # The payload we are sending to Ollama
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False  # We want the whole answer at once, not word-by-word
    }
    
    try:
        # Send the request to our local GPU
        response = requests.post(OLLAMA_URL, json=payload)
        
        # If the request was successful, parse the JSON and return the text
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error from Ollama: {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Is the Ollama app running on your computer?"

# Quick test if you run this file directly
if __name__ == "__main__":
    question = "What is the core idea of Atomic Habits in one sentence?"
    print(f"Asking AI: {question}")
    answer = ask_ai(question)
    print(f"AI Response: {answer}")