import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

async def evaluate_speech(audio_file_path: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        return "⚠️ AI baholash xizmati ulanmagan (OPENAI_API_KEY topilmadi)."

    # Voice to Text
    with open(audio_file_path, "rb") as audio:
        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio
        )

    # Evaluation
    prompt = (
        "You are an IELTS Speaking Examiner. Evaluate the following transcribed audio answer:\n"
        "1. Band scores for Fluency, Vocabulary, Grammar, Pronunciation.\n"
        "2. Estimated Overall Score.\n"
        "3. Clear feedback on mistakes.\n\n"
        f"Transcribed Text: {transcript.text}"
    )

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return f"📝 **Transkript:** {transcript.text}\n\n📊 **AI Examiner Feedback:**\n\n{response.choices[0].message.content}"