import sys
import os
import time
import json
import sqlite3
from newspaper import Article
from bs4 import BeautifulSoup
import requests

def extract_with_newspaper(url):
    """Try to extract article using newspaper3k."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return {
            "title": article.title or "",
            "author": ", ".join(article.authors) if article.authors else "",
            "publication_date": (
                article.publish_date.strftime("%Y-%m-%d")
                if article.publish_date
                else ""
            ),
            "text": article.text or "",
        }
    except Exception as e:
        print(f"[WARN] Newspaper3k failed for {url}: {e}")
        return None

def extract_with_bs4(url):
    """Fallback extraction using BeautifulSoup."""
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text() for p in paragraphs)
        title = soup.title.string.strip() if soup.title else ""
        return {"title": title, "author": "", "publication_date": "", "text": text}
    except Exception as e:
        print(f"[WARN] BS4 fallback failed for {url}: {e}")
        return None

def extract_article(url):
    """Try both methods."""
    data = extract_with_newspaper(url)
    if data and len(data["text"]) > 300:
        return data
    return extract_with_bs4(url)

def create_db(db_path):
    """Create SQLite database and table if they don't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            source_type TEXT,
            source_name TEXT,
            url TEXT UNIQUE,
            title TEXT,
            author TEXT,
            publication_date TEXT,
            text TEXT
        )
    """)
    conn.commit()
    return conn

def scrape_topic(topic, delay=1.5):
    input_path = os.path.join("sources", f"{topic}.json")
    output_dir = "source-data"
    db_path = os.path.join(output_dir, f"{topic}.db")

    if not os.path.exists(input_path):
        print(f"Source file not found: {input_path}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    print(f"Loading sources from {input_path} ...")
    
    with open(input_path, "r", encoding="utf-8") as f:
        sources = json.load(f)

    conn = create_db(db_path)
    cursor = conn.cursor()
    inserted_count = 0

    for source_type, orgs in sources.items():
        for org_name, org_data in orgs.items():
            urls = org_data.get("articles", [])
            for url in urls:
                print(f"[INFO] Scraping: {org_name} → {url}")
                data = extract_article(url)
                if data and data["text"].strip():
                    try:
                        cursor.execute("""
                            INSERT OR IGNORE INTO articles
                            (topic, source_type, source_name, url, title, author, publication_date, text)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            topic,
                            source_type,
                            org_name,
                            url,
                            data["title"],
                            data["author"],
                            data["publication_date"],
                            data["text"]
                        ))
                        conn.commit()
                        inserted_count += 1
                    except Exception as e:
                        print(f"[ERROR] Failed to insert {url}: {e}")
                else:
                    print(f"[ERROR] Failed to extract content for {url}")
                time.sleep(delay)

    conn.close()
    print(f"\nDone! Inserted {inserted_count} articles into {db_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python source-scraping.py <topic>")
        sys.exit(1)

    topic = sys.argv[1].strip().lower()
    scrape_topic(topic)
