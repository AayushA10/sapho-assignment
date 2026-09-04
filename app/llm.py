import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. "
        "Add it to your .env file before running the app."
    )


client = Groq(
    api_key=GROQ_API_KEY
)


MODEL_NAME = "openai/gpt-oss-20b"


def generate_sapho_response(
    post_text: str,
) -> str:
    system_prompt = """
You write thoughtful LinkedIn comments on behalf of Sapho Bio.

Sapho Bio develops rapid microbiology release technology
for precision medicine and pharmaceutical manufacturing.

Your responses must:
- Be professional and credible.
- Add genuine value to the discussion.
- Be specific to the post.
- Be 2 to 4 sentences.
- Avoid unsupported scientific or regulatory claims.
- Avoid sales-heavy or promotional language.
- Avoid generic phrases such as "Great post!".
- Avoid emojis.
- Avoid hashtags unless absolutely necessary.
- Never mention AI or that the response was generated.
- Return only the LinkedIn comment.
"""

    user_prompt = f"""
Write a Sapho Bio LinkedIn response to this post:

{post_text}
"""

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.4,
        max_completion_tokens=500,
        reasoning_effort="low",
        include_reasoning=False,
        stream=False,
    )

    if not completion.choices:
        raise RuntimeError(
            "Groq returned no completion choices."
        )

    message = completion.choices[0].message

    response_text = message.content

    if not response_text:
        raise RuntimeError(
            "Groq returned an empty final response."
        )

    return response_text.strip()