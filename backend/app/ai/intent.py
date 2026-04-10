from openai import OpenAI
import json

client = OpenAI()

PROMPT = """
You are a call center NLU agent.

Classify the intent of this call:
- booking
- faq
- emergency
- general_inquiry

Extract structured information in JSON:
{
 "intent": "...",
 "priority": "normal | high | emergency",
 "customer": {"name": "..."},
 "service": "...",
 "slot": "yyyy-mm-dd HH:MM or null"
}

Transcript:
{transcript}
"""

def classify_intent(transcript: str):
    full_prompt = PROMPT + "\n\nTranscript:\n" + transcript.strip()

    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            # {"role": "user", "content": PROMPT.format(transcript=transcript)}
            {"role": "user", "content": full_prompt}
        ]
    )

    output = completion.choices[0].message.content.strip()

    try:
        return json.loads(output)
    except Exception:
        return {
            "intent": "general_inquiry",
            "priority": "normal",
            "customer": {},
            "service": None,
            "slot": None
        }
