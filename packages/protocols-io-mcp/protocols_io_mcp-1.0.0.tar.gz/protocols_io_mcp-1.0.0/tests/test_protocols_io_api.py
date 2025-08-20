import pytest
from protocols_io_mcp.utils import helpers

@pytest.mark.asyncio
async def test_get_profile():
    """
    Test the get profile feature of the protocols.io API.
    """
    profile = await helpers.access_protocols_io_resource("GET", "/v3/session/profile")
    assert isinstance(profile, dict)
    assert "user" in profile
    assert "name" in profile["user"]
    assert "username" in profile["user"]
    assert "affiliation" in profile["user"]

@pytest.mark.asyncio
async def test_get_public_protocols():
    """
    Test the get public protocols feature of the protocols.io API.
    """
    response = await helpers.access_protocols_io_resource("GET", "/v3/protocols?filter=public&key=dna&page_size=3")
    assert isinstance(response, dict)
    assert "items" in response
    protocols = response["items"]
    assert isinstance(protocols, list)
    assert len(protocols) > 0
    for protocol in protocols:
        assert isinstance(protocol, dict)
        assert "id" in protocol
        assert "title" in protocol
        assert "description" in protocol
        assert "guidelines" in protocol
        assert "before_start" in protocol
        assert "warning" in protocol
        assert "materials_text" in protocol
        assert "doi" in protocol
        assert "public" in protocol
        assert "url" in protocol
        assert "created_on" in protocol
        assert "published_on" in protocol