import os
import json
from openai import OpenAI

# System-Prompt zur strukturierten Extraktion
system_prompt = """
Du bist ein Rezept-Extraktionsassistent.
Extrahiere aus dem Benutzertext ein JSON mit folgendem Format:
{
  "name": "Rezeptname",
  "beschreibung": "Zubereitungsschritte",
  "zutaten": [
    {"name": "Zutat1", "menge": 100},
    {"name": "Zutat2", "menge": 2}
  ]
}
Antworte ausschließlich mit JSON.
"""

def extrahiere_rezept_daten(text: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY nicht gesetzt")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0
    )

    antwort = response.choices[0].message.content

    try:
        return json.loads(antwort)
    except json.JSONDecodeError as e:
        raise ValueError(f"Fehler beim Parsen der JSON-Antwort: {e}\nAntwort war:\n{antwort}")
