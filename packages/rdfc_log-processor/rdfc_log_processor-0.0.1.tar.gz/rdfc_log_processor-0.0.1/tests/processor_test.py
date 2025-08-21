import pytest
import logging
from unittest.mock import AsyncMock

import rdfc_log_processor.processor as processor


class DummyReader:
    """A dummy async reader that yields a sequence of strings."""
    def __init__(self, messages):
        self._messages = messages

    async def strings(self):
        for msg in self._messages:
            yield msg


# --- Tests for Log Processor ---
@pytest.mark.asyncio
async def test_log_transform_writes_and_closes_writer(caplog):
    messages = ["hello", "world"]
    reader = DummyReader(messages)
    writer = AsyncMock()

    args = processor.LogArgs(reader=reader, writer=writer, label="test", level="info", raw=False)
    proc = processor.Log(args)

    caplog.set_level(logging.DEBUG)

    await proc.transform()

    # Check that writer.string was called for each message
    assert [call.args[0] for call in writer.string.await_args_list] == messages

    # Writer.close should be called
    writer.close.assert_awaited_once()

    # Should log the "done reading" message
    assert "done reading so closed writer." in caplog.text


@pytest.mark.asyncio
async def test_log_transform_raw_print(monkeypatch):
    messages = ["one", "two"]
    reader = DummyReader(messages)
    writer = AsyncMock()

    args = processor.LogArgs(reader=reader, writer=writer, raw=True)
    proc = processor.Log(args)

    printed = []
    monkeypatch.setattr("builtins.print", lambda m: printed.append(m))

    await proc.transform()

    # Should have printed each message
    assert printed == messages

    # Writer should still echo messages
    assert [call.args[0] for call in writer.string.await_args_list] == messages


@pytest.mark.asyncio
async def test_log_transform_without_writer(caplog):
    messages = ["foo"]
    reader = DummyReader(messages)

    args = processor.LogArgs(reader=reader, writer=None)
    proc = processor.Log(args)

    caplog.set_level(logging.INFO)

    await proc.transform()

    # Should log message even without writer
    assert "foo" in caplog.text


# --- Tests for Send Processor ---
@pytest.mark.asyncio
async def test_send_produce_sends_messages_and_closes_writer(caplog):
    messages = ["msg1", "msg2", "msg3"]
    writer = AsyncMock()

    args = processor.SendArgs(msgs=messages, writer=writer)
    proc = processor.Send(args)

    caplog.set_level(logging.DEBUG)

    await proc.produce()

    # Verify messages were sent to writer
    assert [call.args[0] for call in writer.string.await_args_list] == messages

    # Verify writer was closed
    writer.close.assert_awaited_once()

    # Verify debug log contains closing statement
    assert "done sending messages so closed writer." in caplog.text
