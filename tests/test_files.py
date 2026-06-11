"""Tests for mtv_agent.server.mcp.files."""

import pytest

from mtv_agent.server.mcp.files import FilesServer


@pytest.fixture
def files():
    return FilesServer()


def test_list_tools(files):
    tools = files.list_tools()
    assert len(tools) == 3
    names = [t["name"] for t in tools]
    assert "list_files" in names
    assert "read_file" in names
    assert "write_file" in names


@pytest.mark.asyncio
async def test_list_files_cwd(files):
    result = await files.call_tool("list_files", {})
    assert isinstance(result, str)
    assert result != "(empty directory)"


@pytest.mark.asyncio
async def test_list_files_nonexistent(files):
    result = await files.call_tool("list_files", {"path": "/nonexistent_xyz"})
    assert "Error" in result


@pytest.mark.asyncio
async def test_list_files_recursive(files, tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "file.txt").write_text("hi")
    result = await files.call_tool(
        "list_files", {"path": str(tmp_path), "recursive": True}
    )
    assert "sub/" in result
    assert "sub/file.txt" in result


@pytest.mark.asyncio
async def test_read_file(files, tmp_path):
    f = tmp_path / "hello.txt"
    f.write_text("line1\nline2\nline3\n")
    result = await files.call_tool("read_file", {"path": str(f)})
    assert "line1" in result
    assert "line3" in result


@pytest.mark.asyncio
async def test_read_file_with_offset_and_limit(files, tmp_path):
    f = tmp_path / "lines.txt"
    f.write_text("a\nb\nc\nd\ne\n")
    result = await files.call_tool(
        "read_file", {"path": str(f), "offset": 2, "limit": 2}
    )
    assert "b" in result
    assert "c" in result
    assert "a" not in result
    assert "d" not in result


@pytest.mark.asyncio
async def test_read_file_not_found(files):
    result = await files.call_tool("read_file", {"path": "/nonexistent_xyz.txt"})
    assert "Error" in result


@pytest.mark.asyncio
async def test_read_file_empty_path(files):
    result = await files.call_tool("read_file", {"path": ""})
    assert "Error" in result


@pytest.mark.asyncio
async def test_write_file(files, tmp_path):
    f = tmp_path / "output.txt"
    result = await files.call_tool(
        "write_file", {"path": str(f), "content": "hello world"}
    )
    assert "Successfully" in result
    assert f.read_text() == "hello world"


@pytest.mark.asyncio
async def test_write_file_creates_parents(files, tmp_path):
    f = tmp_path / "a" / "b" / "c.txt"
    result = await files.call_tool("write_file", {"path": str(f), "content": "nested"})
    assert "Successfully" in result
    assert f.read_text() == "nested"


@pytest.mark.asyncio
async def test_write_file_missing_content(files):
    result = await files.call_tool("write_file", {"path": "/tmp/test.txt"})
    assert "Error" in result


@pytest.mark.asyncio
async def test_unknown_tool(files):
    result = await files.call_tool("unknown", {})
    assert "Unknown tool" in result
