"""第1回: 素のLLMに1回だけ質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする

ツールも会話履歴も持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse
import sys

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"

def chat_loop(initial_question: str) -> None:
    client = genai.Client(api_key=get_api_key())
    
    # 1. 会話履歴を自動で保持する「チャットセッション」を作成
    chat = client.chats.create(model=MODEL)
    
    question = initial_question

    # 2. 継続的に質問できるように無限ループ（while True）を作成
    while True:
        # 質問が空の場合はユーザーに入力を促す
        if not question:
            try:
                question = input("\nあなた: ")
            except (KeyboardInterrupt, EOFError):
                print("\n終了します。")
                break
                
        # 終了コマンドの処理
        if question.lower() in ['exit', 'quit', '終了']:
            print("\n終了します。")
            break

        print(f"\n[質問] {question}")

        try:
            # 3. generate_content ではなく、chat.send_message で質問を送信
            response = chat.send_message(question)

            usage = response.usage_metadata
            if usage is not None:
                print(f"[トークン数] 入力: {usage.prompt_token_count}, 出力: {usage.candidates_token_count}")

            print(f"\nAI: {response.text}")

        except errors.APIError as e:
            print(api_error_message(e.code, e.message))
            sys.exit(1)

        # 次の入力待ちのために質問内容をリセットする
        question = ""

def main() -> None:
    parser = argparse.ArgumentParser(description="LLMと継続的にチャットする")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    print("チャットを開始します。（終了するには 'exit' または '終了' と入力、もしくは Ctrl+C）")
    
    # チャットループを開始
    chat_loop(args.question)

if __name__ == "__main__":
    main()