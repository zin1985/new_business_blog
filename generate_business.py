
import os
import json
import datetime
import requests

USED_FILE = "used_business_terms.json"
POST_DIR = "_posts"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def load_used_terms():
    if not os.path.exists(USED_FILE):
        return []
    with open(USED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_used_terms(terms):
    with open(USED_FILE, "w", encoding="utf-8") as f:
        json.dump(terms, f, ensure_ascii=False, indent=2)

def get_business_article(api_key, used_terms):
    prompt = f"""
以下の条件に従って、ビジネス用語（PDCA, SWOT分析, 4Pなど）をランダムに1つ選び、
その内容についてMarkdownブログ記事として出力してください。
すでに使った用語は: {", ".join(used_terms[-20:]) if used_terms else "なし"}

条件:
- 選んだ用語はタイトルの冒頭に記載（例: "# PDCAとは何か？"）
- 同じ用語は選ばないこと
- 構成は以下の見出しを含むこと
  - 用語の定義
  - 活用方法と具体例
  - メリットとデメリット
  - 図解や表があれば含める
  - 関連用語との違い
  - 実務で使う際のポイント
- 各セクションは200字以上
- 全体で3000字以上
- コードブロック、表、図解風、リンクなどMarkdown記法を活用すること
"""

    headers = { "Content-Type": "application/json" }
    params = { "key": api_key }
    body = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    res = requests.post(API_URL, headers=headers, params=params, json=body)
    if res.status_code != 200:
        raise Exception("Gemini API Error:", res.text)

    data = res.json()
    return data['candidates'][0]['content']['parts'][0]['text']

def extract_term(content):
    import re
    match = re.search(r"#\s*(.+?)とは", content)
    return match.group(1).strip() if match else None

def save_post(content, term):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"{POST_DIR}/{today}-{term.lower().replace(' ', '-')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def generate_post():
    print("🚀 Business Blog Generator 起動")
    os.makedirs(POST_DIR, exist_ok=True)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not set")

    used = load_used_terms()
    for i in range(10):
        content = get_business_article(api_key, used)
        print("📦 Gemini応答内容取得完了")
        term = extract_term(content)
        if term and term not in used:
            print(f"✅ 新しい用語を生成: {term}")
            save_post(content, term)
            used.append(term)
            save_used_terms(used)
            return
        else:
            print(f"⚠️ 用語重複または抽出失敗: {term} ({i+1}/10)")

    raise Exception("❌ 有効な用語を取得できませんでした")

if __name__ == "__main__":
    generate_post()
