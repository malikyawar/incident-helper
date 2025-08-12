import subprocess
import os
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class LLMProvider(ABC):
    @abstractmethod
    def ask(self, prompt: str, context: Dict[str, Any] = None) -> str:
        pass

class OllamaProvider(LLMProvider):
    def __init__(self, model: str = "mistral"):
        self.model = model
    
    def ask(self, prompt: str, context: Dict[str, Any] = None) -> str:
        try:
            # Check if Ollama is running
            check_result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if check_result.returncode != 0:
                return "❌ Ollama is not running. Please start Ollama first."
            
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return f"❌ Ollama error: {result.stderr}"
                
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "❌ Request timed out. The model might be taking too long to respond."
        except FileNotFoundError:
            return "❌ Ollama not found. Please install Ollama first."
        except Exception as e:
            return f"❌ Error: {e}"

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
    def ask(self, prompt: str, context: Dict[str, Any] = None) -> str:
        if not self.api_key:
            return "❌ OpenAI API key not found. Set OPENAI_API_KEY environment variable."
        
        try:
            import openai
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except ImportError:
            return "❌ OpenAI library not installed. Run: pip install openai"
        except Exception as e:
            return f"❌ OpenAI error: {e}"

class LLMEngine:
    def __init__(self, provider: str = "ollama", model: str = None):
        self.provider_name = provider
        
        if provider == "ollama":
            self.provider = OllamaProvider(model or "mistral")
        elif provider == "openai":
            self.provider = OpenAIProvider(model or "gpt-3.5-turbo")
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def ask(self, prompt: str, context: Dict[str, Any] = None) -> str:
        return self.provider.ask(prompt, context)
    
    def get_provider_info(self) -> str:
        return f"Using {self.provider_name} provider"
