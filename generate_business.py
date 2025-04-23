import os
import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_post():
    today = datetime.date.today()
    prompt = f"""
あなたはビジネスフレームワークの専門家です。
本日は最新のビジネス手法や分析フレームワークについて図解と実例付きでブログ記事をMarkdown形式で出力してください。
構成：
- タイトル
- 定義と目的
- 活用方法
- 図解の言語説明
- 実例
- 関連手法
- まとめ
"""

    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたはビジネスフレームワークの専門家です。"},
            {"role": "user", "content": prompt}
        ]
    )

    content = res.choices[0].message.content
    filename = f"_posts/{today}-business-framework.md"
    with open(filename, "w") as f:
        f.write(content)

if __name__ == "__main__":
    generate_post()
