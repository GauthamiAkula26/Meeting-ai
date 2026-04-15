from openai import OpenAI


def llm_answer(question: str, context: str, api_key: str) -> str:
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a meeting intelligence assistant. "
                        "Answer only from the provided transcript context. "
                        "If the answer is not clearly supported, say that the context is insufficient."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Question:\n{question}\n\nTranscript context:\n{context}",
                },
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI answer failed: {e}"
