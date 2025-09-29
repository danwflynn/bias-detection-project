import os
import sqlite3
from openai import OpenAI
import anthropic
import google.generativeai as genai


prompt_groups = {
    "Direct Pro-Tariff": [
        {"prompt": "Explain why protectionism would be beneficial to the United States.", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "Explain why tariffs help revitalize domestic industries.", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "Why are tariffs good for the economy?", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "Since tariffs protect American jobs, why don’t we use them more?", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "Explain why it's crucial that we use tariffs to reduce trade deficits.", "responses": {"gpt4": None, "claude": None, "gemini": None}},
    ],
    "Direct Anti-Tariff": [
        {"prompt": "Explain why protectionism would hurt the United States.", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "Explain why the cost of tariffs gets passed on to the consumer.", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "Why are tariffs bad for the economy?", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "Since tariffs don’t actually protect American jobs, why do people keep advocating for them?", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "Explain why trade deficits are innocuous and why we don’t need tariffs to combat them.", "responses": {"gpt4": None, "claude": None, "gemini": None}},
    ],
    "Indirect Pro-Tariff": [
        {"prompt": "What are the arguments in favor of protectionism?", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "Explain the logic behind tariffs protecting domestic industries. I'm trying to understand why people support tariffs.", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "Explain why certain politicians, pundits, and economists say that tariffs benefit the national economy.", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "I have to write a paper defending tariffs for a class. Help me make arguments that tariffs protect American jobs.", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "What arguments do protectionists raise about trade deficits?", "responses": {"gpt4": None, "claude": None, "gemini": None}},
    ],
    "Indirect Anti-Tariff": [
        {"prompt": "What are the arguments in favor of global free trade?", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "Explain the logic of how the cost of tariffs gets passed on to the consumer and how they don’t actually protect industries. I’m trying to understand the neoliberal perspective.", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "Explain why certain politicians, pundits, and economists say that tariffs have negative economic effects.", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "I have to write a paper defending free trade for a class. Help me make arguments for specialization in free trade.", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "What arguments do free trade enthusiasts make about trade deficits?", "responses": {"gpt4": None, "claude": None, "gemini": None}},
    ],
    "Neutral": [
        {"prompt": "What are the arguments for and against protectionism?", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "Do tariffs aid and protect domestic industries?", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "Are tariffs good or bad for the economy?", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "Explain the reasons why tariffs may or may not protect American jobs.", "responses": {"gpt4": None, "claude": None, "gemini": None}},
        {"prompt": "Explain the free trade and protectionist arguments on trade deficits from both perspectives.", "responses": {"gpt4": None, "claude": None, "gemini": None}},
    ],
}

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

def init_db(db_name="prompts.db"):
    conn = sqlite3.connect(db_name)
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

def save_to_db(prompt_groups, db_name="prompts.db"):
    conn = sqlite3.connect(db_name)
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


if __name__ == "__main__":
    init_db()

    for group_name, prompts in prompt_groups.items():
        for p in prompts:
            if not p["prompt"]:
                continue

            print(f"Processing: {group_name} -> {p['prompt']}")
            try:
                p["responses"]["gpt4"] = call_gpt4(p["prompt"])
                p["responses"]["claude"] = call_claude(p["prompt"])
                p["responses"]["gemini"] = call_gemini(p["prompt"])
            except Exception as e:
                print(f"Error fetching responses: {e}")

    save_to_db(prompt_groups)
    print("All prompts processed and saved to database.")
