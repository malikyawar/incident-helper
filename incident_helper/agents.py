import subprocess

class LLMEngine:
    def __init__(self, model="mistral"):
        self.model = model

    def ask(self, prompt: str) -> str:
        try:
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True, text=True
            )
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {e}"
