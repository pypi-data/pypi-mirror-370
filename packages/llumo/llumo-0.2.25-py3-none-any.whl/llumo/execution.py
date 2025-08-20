import openai
import google.generativeai as genai
from .models import Provider

class ModelExecutor:
    def __init__(self, apiKey: str):
        self.apiKey = apiKey

    def execute(self, provider: Provider, modelName: str, prompt: str,api_key) -> str:
        if provider == Provider.OPENAI:
            return self._executeOpenAI(modelName, prompt,api_key)
        elif provider == Provider.GOOGLE:
            return self._executeGoogle(modelName, prompt,api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _executeOpenAI(self, modelName: str, prompt: str,api_key) -> str:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(model="gpt-4",  # Replace with the desired model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}  # User's prompt
            ]
        )
        return response.choices[0].message.content

    def _executeGoogle(self, modelName: str, prompt: str,api_key) -> str:

        # Configure GenAI with API Key
        genai.configure(api_key=api_key)

        # Select Generative Model
        model = genai.GenerativeModel("gemini-2.0-flash-lite")
        # Generate Response
        response = model.generate_content(prompt)
        return response.text


