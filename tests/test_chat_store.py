"""Tests for mtv_agent.server.chat.store."""

import tempfile

from mtv_agent.server.chat.store import ChatStore


def test_save_and_get():
    with tempfile.TemporaryDirectory() as d:
        store = ChatStore(d)
        store.save("abc", [{"role": "user", "content": "hello"}])
        chat = store.get("abc")
        assert chat is not None
        assert chat["id"] == "abc"
        assert chat["title"] == "hello"
        assert len(chat["messages"]) == 1


def test_list():
    with tempfile.TemporaryDirectory() as d:
        store = ChatStore(d)
        store.save("a", [{"role": "user", "content": "first"}])
        store.save("b", [{"role": "user", "content": "second"}])
        chats = store.list()
        assert len(chats) == 2
        ids = {c["id"] for c in chats}
        assert ids == {"a", "b"}


def test_delete():
    with tempfile.TemporaryDirectory() as d:
        store = ChatStore(d)
        store.save("x", [{"role": "user", "content": "bye"}])
        assert store.delete("x") is True
        assert store.get("x") is None
        assert store.delete("x") is False


def test_get_missing():
    with tempfile.TemporaryDirectory() as d:
        store = ChatStore(d)
        assert store.get("nonexistent") is None


def test_title_truncation():
    with tempfile.TemporaryDirectory() as d:
        store = ChatStore(d)
        long_msg = "a" * 200
        store.save("t", [{"role": "user", "content": long_msg}])
        chat = store.get("t")
        assert len(chat["title"]) < 200
        assert chat["title"].endswith("...")
