import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Ovozni matnga o'girish (Whisper)
async def transcribe_audio(file_path: str) -> str:
    with open(file_path, "rb") as audio_file:
        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text

# Matnni ovozga o'girish (TTS)
async def text_to_speech(text: str, output_path: str):
    response = await client.audio.speech.create(
        model="tts-1",
        voice="alloy", # Ovoz turi: alloy, echo, fable, onyx, nova, shimmer
        input=text
    )
    response.stream_to_file(output_path)