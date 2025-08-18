import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.tools import BaseTool
from langchain_mcp_tools.langchain_mcp_tools import (
    convert_mcp_to_langchain_tools,
)

# Fix the asyncio mark warning by installing pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture
def mock_stdio_client():
    with patch('langchain_mcp_tools.langchain_mcp_tools.stdio_client') as mock:
        mock.return_value.__aenter__.return_value = (AsyncMock(), AsyncMock())
        yield mock


@pytest.fixture
def mock_client_session():
    with patch('langchain_mcp_tools.langchain_mcp_tools.ClientSession') \
            as mock:
        session = AsyncMock()
        # Mock the list_tools response
        session.list_tools.return_value = MagicMock(
            tools=[
                MagicMock(
                    name="tool1",
                    description="Test tool",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]
        )
        mock.return_value.__aenter__.return_value = session
        yield mock


@pytest.mark.asyncio
async def test_convert_mcp_to_langchain_tools_empty():
    server_configs = {}
    tools, cleanup = await convert_mcp_to_langchain_tools(server_configs)
    assert isinstance(tools, list)
    assert len(tools) == 0
    await cleanup()


"""
@pytest.mark.asyncio
async def test_convert_mcp_to_langchain_tools_invalid_config():
    server_configs = {"invalid": {"command": "nonexistent"}}
    with pytest.raises(Exception):
        await convert_mcp_to_langchain_tools(server_configs)
"""


"""
@pytest.mark.asyncio
async def test_convert_single_mcp_success(
    mock_stdio_client,
    mock_client_session
):
    # Test data
    server_name = "test_server"
    server_config = {
        "command": "test_command",
        "args": ["--test"],
        "env": {"TEST_ENV": "value"}
    }
    langchain_tools = []
    ready_event = asyncio.Event()
    cleanup_event = asyncio.Event()

    # Create task
    task = asyncio.create_task(
        convert_single_mcp_to_langchain_tools(
            server_name,
            server_config,
            langchain_tools,
            ready_event,
            cleanup_event
        )
    )

    # Wait for ready event
    await asyncio.wait_for(ready_event.wait(), timeout=1.0)

    # Verify tools were created
    assert len(langchain_tools) == 1
    assert isinstance(langchain_tools[0], BaseTool)
    assert langchain_tools[0].name == "tool1"

    # Trigger cleanup
    cleanup_event.set()
    await task
"""


@pytest.mark.asyncio
async def test_convert_mcp_to_langchain_tools_multiple_servers(
    mock_stdio_client,
    mock_client_session
):
    server_configs = {
        "server1": {"command": "cmd1", "args": []},
        "server2": {"command": "cmd2", "args": []}
    }

    tools, cleanup = await convert_mcp_to_langchain_tools(server_configs)

    # Verify correct number of tools created
    assert len(tools) == 2  # One tool per server
    assert all(isinstance(tool, BaseTool) for tool in tools)

    # Test cleanup
    await cleanup()


"""
@pytest.mark.asyncio
async def test_tool_execution(mock_stdio_client, mock_client_session):
    server_configs = {
        "test_server": {"command": "test", "args": []}
    }

    # Mock the tool execution response
    session = mock_client_session.return_value.__aenter__.return_value
    session.call_tool.return_value = MagicMock(
        isError=False,
        content={"result": "success"}
    )

    tools, cleanup = await convert_mcp_to_langchain_tools(server_configs)

    # Test tool execution
    result = await tools[0]._arun(test_param="value")
    assert result == {"result": "success"}

    # Verify tool was called with correct parameters
    session.call_tool.assert_called_once_with("tool1", {"test_param": "value"})

    await cleanup()
"""


@pytest.mark.asyncio
async def test_tool_execution_error(mock_stdio_client, mock_client_session):
    server_configs = {
        "test_server": {"command": "test", "args": []}
    }

    # Mock error response
    session = mock_client_session.return_value.__aenter__.return_value
    session.call_tool.return_value = MagicMock(
        isError=True,
        content="Error message"
    )

    tools, cleanup = await convert_mcp_to_langchain_tools(server_configs)

    # Test tool execution error
    with pytest.raises(Exception):
        await tools[0]._arun(test_param="value")

    await cleanup()
