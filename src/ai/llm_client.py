import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
class LLMClient:
    @staticmethod
    def ask(prompt: str) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI document understanding engine."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message["content"]
