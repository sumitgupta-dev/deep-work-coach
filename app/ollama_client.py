import requests

# Your local Ollama server address
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
EMBEDDING_URL = "http://127.0.0.1:11434/api/embeddings"
MODEL_NAME = "llama3.2:1b"
EMBEDDING_MODEL = "nomic-embed-text"

def ask_ai(prompt: str):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error from Ollama: {response.text}"
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Is the Ollama app running?"

def get_embedding(text: str):
    """Convert a piece of text into a vector (list of floats)."""
    payload = {
        "model": EMBEDDING_MODEL,
        "prompt": text
    }
    response = requests.post(EMBEDDING_URL, json=payload)
    if response.status_code == 200:
        return response.json()["embedding"]
    else:
        raise Exception(f"Embedding error: {response.text}")

if __name__ == "__main__":
    # Quick test
    vec = get_embedding("Deep work is valuable.")
    print(f"Embedding length: {len(vec)}")  # Should print 768
    print(f"First 5 values: {vec[:5]}")