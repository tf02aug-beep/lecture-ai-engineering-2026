from types import SimpleNamespace
import sys

import app.ask as ask_module


def test_ask_prints_token_usage_and_returns_text(capsys):
    response = SimpleNamespace(
        text="answer",
        usage_metadata=SimpleNamespace(
            prompt_token_count=12,
            candidates_token_count=5,
        ),
    )
    chat = SimpleNamespace(send_message=lambda question: response)

    assert ask_module.ask(chat, "question") == "answer"
    assert capsys.readouterr().out.strip() == "[トークン使用量] 入力: 12 / 出力: 5"


def test_main_reuses_chat_for_follow_up_questions(monkeypatch):
    class FakeChat:
        def __init__(self):
            self.questions = []

        def send_message(self, question):
            self.questions.append(question)
            return SimpleNamespace(text="answer", usage_metadata=None)

    chat = FakeChat()

    class FakeClient:
        def __init__(self, api_key):
            self.chats = SimpleNamespace(
                create=lambda model: chat,
            )

    answers = iter(["follow-up", "exit"])
    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(sys, "argv", ["app.ask", "first question"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    ask_module.main()

    assert chat.questions == ["first question", "follow-up"]