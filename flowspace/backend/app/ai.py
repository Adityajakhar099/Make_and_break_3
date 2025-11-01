import os
from typing import Dict
# optional OpenAI usage; fallback to a simple heuristic

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class AITaskProcessor:
    def __init__(self, openai_client=None):
        self.client = openai_client

    def extract_task_from_email(self, email_content: str) -> Dict:
        """
        Minimal heuristic: first line -> title; rest -> description.
        If OPENAI_API_KEY is set and openai is installed, tries to call OpenAI (optional).
        """
        if OPENAI_API_KEY:
            try:
                import openai
                openai.api_key = OPENAI_API_KEY
                prompt = f"Extract a task from the following email. Return JSON with title and description.\n\n{email_content}"
                resp = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":prompt}],
                    max_tokens=200,
                )
                text = resp.choices[0].message.content
                import json
                try:
                    return json.loads(text)
                except Exception:
                    pass
            except Exception:
                pass
        # fallback simple
        lines = [l.strip() for l in email_content.splitlines() if l.strip()]
        title = lines[0] if lines else "New Task"
        desc = "\n".join(lines[1:]) if len(lines) > 1 else ""
        return {"title": title, "description": desc}
