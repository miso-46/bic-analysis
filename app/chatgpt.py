# chatgpt.py
from openai import OpenAI
import pandas as pd
import os

client = OpenAI()

api_key = os.getenv("OPENAI_API_KEY")

def interpret_corr_matrix(corr_matrix: pd.DataFrame, model: str = "gpt-4o-mini") -> str:
    # 相関行列を文字列に変換（CSV形式で出力）
    corr_str = corr_matrix.to_csv(index=True)
    # ChatGPT に投げるプロンプトを作成
    prompt = f"""以下の相関行列に基づいて、どの変数間に強い相関があるか、またその相関が意味する内容について詳細に解釈してください。
    
相関行列:
{corr_str}
"""
    # OpenAI API を呼び出す
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "あなたは統計解析とデータサイエンスに精通した専門家です。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    interpretation = response.choices[0].message.content.strip()
    return interpretation

