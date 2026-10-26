"""会話履歴を保ったままLLMと連続してチャットするスクリプト。

使い方:
    uv run python -m app.chat "LoRAとは何ですか？"
    uv run python -m app.chat            # 質問を省略すると、講座に固有の質問からスタートする

チャットモードに入り、会話履歴を踏まえた回答ができるようになります。
「終了」または「exit」と入力するか、Ctrl+Cで終了します。
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"
EXIT_COMMANDS = {"exit", "quit", "終了"}


def chat_loop(initial_question: str) -> None:
    client = genai.Client(api_key=get_api_key())
    chat = client.chats.create(model=MODEL)
    question = initial_question

    while True:
        if not question:
            try:
                question = input("\nあなた: ").strip()
            except EOFError:
                print("\n終了します。")
                break

        question = question.strip()
        if not question:
            continue
        if question.casefold() in EXIT_COMMANDS:
            print("\n終了します。")
            break

        print(f"\n[質問] {question}")
        response = chat.send_message(question)

        usage = response.usage_metadata
        if usage is not None:
            print(
                f"[トークン数] 入力: {usage.prompt_token_count}, "
                f"出力: {usage.candidates_token_count}"
            )
        print(f"\nAI: {response.text}")
        question = ""


def main() -> None:
    parser = argparse.ArgumentParser(description="LLMと継続的にチャットする")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    print("チャットを開始します。（終了するには 'exit' または '終了' と入力、もしくは Ctrl+C）")
    try:
        chat_loop(args.question)
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1) from e
    except KeyboardInterrupt:
        print("\n終了します。")


if __name__ == "__main__":
    main()