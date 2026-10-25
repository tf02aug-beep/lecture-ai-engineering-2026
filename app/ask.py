"""第1回: 会話履歴を保ちながら素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする

回答後に続けて質問でき、空行または exit で終了する。
ツールは持たない「素の」呼び出しだが、会話履歴は維持する。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(chat, question: str) -> str:
    response = chat.send_message(question)

    usage = response.usage_metadata
    if usage is None:
        print("[トークン使用量] 情報なし")
    else:
        input_tokens = usage.prompt_token_count
        output_tokens = usage.candidates_token_count
        print(f"[トークン使用量] 入力: {input_tokens} / 出力: {output_tokens}")

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    client = genai.Client(api_key=get_api_key())
    chat = client.chats.create(model=MODEL)
    question = args.question or DEFAULT_QUESTION

    while True:
        print(f"[質問] {question}\n")
        try:
            print(ask(chat, question))
        except errors.APIError as e:
            print(api_error_message(e.code, e.message))
            raise SystemExit(1)

        try:
            question = input("\n次の質問（終了: 空行または exit）> ").strip()
        except EOFError:
            break
        if not question or question.lower() in {"exit", "quit"}:
            break


if __name__ == "__main__":
    main()
