import uuid
import pytest
from protocols_io_mcp.server import mcp
from fastmcp import Client

test_protocol_id = None
test_protocol_title = None
test_protocol_description = None

@pytest.mark.asyncio
async def test_search_public_protocols():
    async with Client(mcp) as client:
        response = await client.call_tool("search_public_protocols", {"keyword": "dna", "page": 3})
        assert "error_message" not in response.data
        assert response.data["current_page"] == 3

@pytest.mark.asyncio
async def test_get_my_protocols():
    async with Client(mcp) as client:
        response = await client.call_tool("get_my_protocols", {})
        assert "error_message" not in response.data
        if len(response.data) == 2:
            global test_protocol_id, test_protocol_title, test_protocol_description
            for protocol in response.data:
                if protocol["doi"] is None:
                    test_protocol_id = protocol["id"]
                    test_protocol_title = protocol["title"]
                    test_protocol_description = protocol["description"]
                    break
            assert test_protocol_id is not None

@pytest.mark.asyncio
async def test_create_protocol():
    global test_protocol_id, test_protocol_title, test_protocol_description
    if test_protocol_id is not None:
        pytest.skip("Skipping because the maximum number of protocols has been reached")
    async with Client(mcp) as client:
        response = await client.call_tool("create_protocol", {"title": "Test Protocol", "description": "This is a test protocol."})
        assert "error_message" not in response.data
        assert response.data["title"] == "Test Protocol"
        assert response.data["description"] == "This is a test protocol."
        test_protocol_id = response.data["id"]
        test_protocol_title = response.data["title"]
        test_protocol_description = response.data["description"]

@pytest.mark.asyncio
async def test_get_protocol():
    global test_protocol_id
    async with Client(mcp) as client:
        response = await client.call_tool("get_protocol", {"protocol_id": test_protocol_id})
        assert "error_message" not in response.data
        assert response.data["id"] == test_protocol_id
        assert response.data["title"] == test_protocol_title
        assert response.data["description"] == test_protocol_description

@pytest.mark.asyncio
async def test_update_protocol_title():
    global test_protocol_id, test_protocol_title
    async with Client(mcp) as client:
        title_updated = f"Updated Test Protocol {uuid.uuid4().hex}"
        response = await client.call_tool("update_protocol_title", {"protocol_id": test_protocol_id, "title": title_updated})
        assert "error_message" not in response.data
        assert response.data["title"] == title_updated
        response = await client.call_tool("update_protocol_title", {"protocol_id": test_protocol_id, "title": test_protocol_title})
        assert "error_message" not in response.data
        assert response.data["title"] == test_protocol_title

@pytest.mark.asyncio
async def test_update_protocol_description():
    global test_protocol_id, test_protocol_description
    async with Client(mcp) as client:
        description_updated = f"Updated description {uuid.uuid4().hex}"
        response = await client.call_tool("update_protocol_description", {"protocol_id": test_protocol_id, "description": description_updated})
        assert "error_message" not in response.data
        assert response.data["description"] == description_updated
        response = await client.call_tool("update_protocol_description", {"protocol_id": test_protocol_id, "description": test_protocol_description})
        assert "error_message" not in response.data
        assert response.data["description"] == test_protocol_description

@pytest.mark.asyncio
async def test_get_protocol_steps():
    global test_protocol_id
    async with Client(mcp) as client:
        response = await client.call_tool("get_protocol_steps", {"protocol_id": test_protocol_id})
        assert "error_message" not in response.data