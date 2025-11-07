import httpx
import json
import asyncio


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2:7b-instruct"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.client = httpx.AsyncClient(timeout=300.0)

    async def generate(self, prompt: str, max_tokens: int = 256):
        """Send prompt to Ollama model and return generated text"""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "options": {"num_predict": max_tokens}
        }

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            # Ollama returns JSON lines, one per stream chunk
            output_text = ""
            for line in response.text.splitlines():
                try:
                    data = json.loads(line)
                    if "response" in data:
                        output_text += data["response"]
                except json.JSONDecodeError:
                    continue
            return output_text.strip() if output_text else response.text

        except Exception as e:
            print(f"⚠️ Ollama request failed: {e}")
            return f"Error: {e}"

    async def aclose(self):
        await self.client.aclose()
