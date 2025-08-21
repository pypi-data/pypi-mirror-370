# unidoc_agent/ollama_client.py
import os
import json
import ollama
from pathlib import Path

class OllamaClient:
    def __init__(self, model="llama3", session_id="default_user"):
        self.model = model
        self.session_id = session_id
        self.cache_dir = Path.home() / ".unidoc_ollama_cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / f"{self.model}_{self.session_id}.json"
        self.history = self.load_history()

    def load_history(self):
        if self.cache_file.exists():
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_history(self):
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)

    def clear_history(self):
        self.history = []
        if self.cache_file.exists():
            self.cache_file.unlink()

    def chat(self, message):
        self.history.append({"role": "user", "content": message})
        try:
            response = ollama.chat(model=self.model, messages=self.history)
            assistant_response = response["message"]["content"]
            self.history.append({"role": "assistant", "content": assistant_response})
            self.save_history()
            return assistant_response
        except Exception as e:
            self.history.pop()  # Remove failed user message
            return f"Error interacting with LLM: {str(e)}"