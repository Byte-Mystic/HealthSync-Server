from gemini import OpenRouter

api_key = "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"


def chat_with_me(question: str) -> str | None:
    try:
        gemma_client = OpenRouter(api_key=api_key, model="google/gemma-7b-it:free")
        response = gemma_client.create_chat_completion(f"{question}")
        return response
    except Exception as e:
        print(f"error in generating Answer: {e}")
        return "Unable to Generate Result"
