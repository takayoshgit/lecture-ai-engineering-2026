from types import SimpleNamespace

from app import chat


def test_chat_loop_keeps_session_for_follow_up_questions(monkeypatch, capsys):
    sent_questions = []

    class FakeChat:
        def send_message(self, question):
            sent_questions.append(question)
            return SimpleNamespace(
                usage_metadata=SimpleNamespace(
                    prompt_token_count=10,
                    candidates_token_count=5,
                ),
                text=f"回答: {question}",
            )

    class FakeChats:
        def create(self, model):
            return FakeChat()

    class FakeClient:
        chats = FakeChats()

    monkeypatch.setattr(chat.genai, "Client", lambda api_key: FakeClient())
    monkeypatch.setattr(chat, "get_api_key", lambda: "test-key")
    answers = iter(("補足して", "exit"))
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    chat.chat_loop("最初の質問")

    output = capsys.readouterr().out
    assert sent_questions == ["最初の質問", "補足して"]
    assert "[トークン数] 入力: 10, 出力: 5" in output
    assert "AI: 回答: 補足して" in output