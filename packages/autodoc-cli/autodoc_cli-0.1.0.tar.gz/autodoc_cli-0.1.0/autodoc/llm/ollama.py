from __future__ import annotations
from dataclasses import dataclass

import requests


@dataclass
class OllamaClient:
    model: str
    base_url: str = "http://localhost:11434"

    def generate_doc(self, language: str, function_name: str, signature: str, body: str) -> str:
        system = (
            "You are a senior engineer. Generate a concise, accurate C doc comment for the given function. "
            "Use the language's idiomatic style and formatting. Do not invent behavior."
        )
        prompt = (
            f"Language: {language}\n"
            f"Function: {function_name}\n"
            f"Signature:\n{signature}\n"
            f"Body:\n{body}\n\n"
            "Write only the doc comment block; do not include the function code."
        )
        # Try generate endpoint
        gen_payload = {"model": self.model, "prompt": prompt, "options": {"num_ctx": 8192}, "stream": False}
        # Some Ollama versions expect system in chat; keep prompt self-contained
        try:
            resp = requests.post(f"{self.base_url}/api/generate", json=gen_payload, timeout=120)
            if resp.status_code == 404:
                raise RuntimeError("generate_not_found")
            resp.raise_for_status()
            out = resp.json()
            text = out.get("response", "")
            if text:
                return text.strip()
        except Exception:
            # Fallback to chat endpoint
            chat_payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "options": {"num_ctx": 8192},
            }
            resp = requests.post(f"{self.base_url}/api/chat", json=chat_payload, timeout=120)
            resp.raise_for_status()
            out = resp.json()
            msg = out.get("message", {})
            content = msg.get("content", "") if isinstance(msg, dict) else ""
            return content.strip()
        # Fallback if neither endpoint yielded content
        return ""

    def is_available(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return r.ok
        except Exception:
            return False


