import os
import sys
import json
import sqlite3
from openai import OpenAI
import anthropic
import google.generativeai as genai


openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def call_gpt4(prompt):
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def call_claude(prompt):
    response = claude_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def call_gemini(prompt):
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prompts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_name TEXT,
        prompt TEXT,
        gpt4_response TEXT,
        claude_response TEXT,
        gemini_response TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_to_db(prompt_groups, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for group_name, prompts in prompt_groups.items():
        for p in prompts:
            cursor.execute(
                "INSERT INTO prompts (group_name, prompt, gpt4_response, claude_response, gemini_response) VALUES (?, ?, ?, ?, ?)",
                (
                    group_name,
                    p["prompt"],
                    p["responses"]["gpt4"],
                    p["responses"]["claude"],
                    p["responses"]["gemini"],
                ),
            )

    conn.commit()
    conn.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python run-prompts.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    if filename.endswith(".json"):
        filename = filename[:-5]

    json_path = os.path.join("prompts", f"{filename}.json")
    db_path = os.path.join("data", f"{filename}.db")

    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        prompt_groups = json.load(f)

    os.makedirs("data", exist_ok=True)

    init_db(db_path)

    for group_name, prompts in prompt_groups.items():
        for p in prompts:
            if not p.get("prompt"):
                continue

            print(f"Processing: {group_name} -> {p['prompt']}")
            try:
                p["responses"]["gpt4"] = call_gpt4(p["prompt"])
                p["responses"]["claude"] = call_claude(p["prompt"])
                p["responses"]["gemini"] = call_gemini(p["prompt"])
            except Exception as e:
                print(f"Error fetching responses: {e}")

    save_to_db(prompt_groups, db_path)
    print(f"All prompts processed and saved to {db_path}")

if __name__ == "__main__":
    main()
