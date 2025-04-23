
import os
import json
import datetime
import requests

USED_TOPICS_FILE = "used_topics.json"
POST_DIR = "_posts"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def load_used_topics():
    if not os.path.exists(USED_TOPICS_FILE):
        return []
    with open(USED_TOPICS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_used_topics(topics):
    with open(USED_TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2, ensure_ascii=False)

def get_topic_article(api_key, used_topics):
    prompt = f"""
次のルールに従って、ビジネス用語を1つランダムに選び、Markdown形式のブログ記事として出力してください。

# 条件
- 使用済みトピック（{', '.join(used_topics[-20:]) if used_topics else 'なし'}）は絶対に使用しないこと
- 重複のないようランダム性を持たせる
- 各セクションは200字以上
- 総文字数は3000字以上
- 表、図、コード、リンクを含めると尚良し
- Markdown形式
- 最初の行に「# 用語名 - 概要」として明記
- 出力全体はMarkdown文書として完結すること

# 構成：
1. 用語と概要（タイトル）
2. 背景と目的
3. 活用方法（できれば図解・表を含めて）
4. メリット・デメリット
5. 他手法との違い
6. 企業導入事例（仮想でもよいが現実味のあるもの）
7. よくある誤解
8. 成功のコツ
9. 今後の展望
10. 関連リンク（可能であれば）

"""

    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    body = {"contents": [{"parts": [{"text": prompt}]}]}

    res = requests.post(API_URL, headers=headers, params=params, json=body)
    if res.status_code != 200:
        raise Exception(f"Gemini API error: {res.status_code} - {res.text}")
    data = res.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("⚠️ Gemini response parse error:", e)
        return None

def extract_topic(content):
    import re
    match = re.search(r"# (.+?) - ", content)
    return match.group(1) if match else None

def sanitize_filename(name):
    import re
    return re.sub(r'[\/:*?"<>|]', '', name)

def save_post(content, topic):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"{POST_DIR}/{today}-{sanitize_filename(topic)}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def generate_post():
    os.makedirs(POST_DIR, exist_ok=True)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not set")

    used_topics = load_used_topics()
    for attempt in range(5):
        print(f"🚀 試行 {attempt + 1}")
        content = get_topic_article(api_key, used_topics)
        if not content:
            print("⚠️ 応答が空、再試行")
            continue
        topic = extract_topic(content)
        print(f"📦 トピック候補:", topic)
        if topic and topic not in used_topics:
            save_post(content, topic)
            used_topics.append(topic)
            save_used_topics(used_topics)
            print("✅ 保存完了")
            return
        print(f"⚠️ 重複または抽出失敗: {topic}")
    raise Exception("❌ トピック取得に失敗しました")

if __name__ == "__main__":
    generate_post()
