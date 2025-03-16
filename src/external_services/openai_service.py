from openai import AsyncOpenAI
from decouple import config

OPENAI_API_KEY = config('OPENAI_API_KEY')

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def make_summarization(note_content: str) -> str:
    messages = [{"role": "system",
                 "content": "You are a helpful assistant who summarizes note content, "
                            "providing only the essential information."},
                {"role": "user",
                 "content": note_content}]

    completion = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.0,
    )
    reply = completion.choices[0].message.content

    return reply
