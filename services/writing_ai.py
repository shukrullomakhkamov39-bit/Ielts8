import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

async def evaluate_essay(essay_text: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        return "⚠️ AI baholash xizmati ulanmagan (OPENAI_API_KEY topilmadi)."

    prompt = (
        "You are an official IELTS Writing Examiner. Evaluate the following essay and provide:\n"
        "1. Band scores for Task Response, Coherence & Cohesion, Lexical Resource, Grammatical Range & Accuracy.\n"
        "2. Overall Band Score.\n"
        "3. Key mistakes and actionable recommendations for improvement.\n\n"
        f"Essay:\n{essay_text}"
    )

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content