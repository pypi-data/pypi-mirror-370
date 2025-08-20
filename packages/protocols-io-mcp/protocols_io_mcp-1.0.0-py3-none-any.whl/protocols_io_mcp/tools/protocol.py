import uuid
from datetime import datetime, timezone
from typing import Annotated
from pydantic import BaseModel, Field
from protocols_io_mcp.server import mcp
import protocols_io_mcp.utils.helpers as helpers

class User(BaseModel):
    username: Annotated[str, Field(description="Unique identifier for the user")]
    name: str
    affiliation: Annotated[str | None, Field(description="Affiliation of the user, if the user is not affiliated, this will be null")] = None

    @classmethod
    def from_api_response(cls, data: dict) -> "User":
        return cls(
            username=data["username"],
            name=data["name"],
            affiliation=data["affiliation"] or None
        )

class Material(BaseModel):
    name: Annotated[str, Field(description="Name of the material")]
    quantity: Annotated[float, Field(description="Amount of material needed", ge=0.0)]
    unit: Annotated[str, Field(description="Unit of measurement for the material, e.g., 'mL', 'g', 'μL'")]

class ProtocolStepInput(BaseModel):
    description: Annotated[str, Field(description="Description of the step")]
    materials: Annotated[list[Material], Field(description="Materials required for this step. Empty if no materials are needed")] = Field(default_factory=list)
    reference_protocol_ids: Annotated[list[int], Field(description="Protocol IDs referenced by this step. Empty if no references exist. Strongly recommend using at least one reference to ensure credibility")] = Field(default_factory=list)

    @staticmethod
    async def to_string(step: "ProtocolStepInput") -> str:
        step_content = f"{step.description}\n"
        if len(step.materials) + len(step.reference_protocol_ids) > 0:
            step_content += "\n"
        # add materials to step content
        if len(step.materials) > 0:
            step_content += "[Materials]\n"
            for material in step.materials:
                step_content += f"- {material.name.replace(' ', '')} {material.quantity} {material.unit.replace(' ', '')}\n"
        # add reference protocols to step content
        if len(step.reference_protocol_ids) > 0:
            if len(step.materials) > 0:
                step_content += "\n"
            step_content += "[Protocol References]\n"
            for protocol_id in step.reference_protocol_ids:
                # get information about the referenced protocol
                response_get_protocol = await helpers.access_protocols_io_resource("GET", f"/v4/protocols/{protocol_id}")
                if response_get_protocol["status_code"] != 0:
                    return response_get_protocol["status_text"]
                protocol = await Protocol.from_protocol_id(response_get_protocol["payload"]["id"])
                step_content += f"- {protocol.title}[{protocol.id}] {protocol.doi}\n"
        return step_content

class ProtocolStep(BaseModel):
    id: Annotated[str, Field(description="Unique identifier for the step")]
    description: Annotated[str, Field(description="Description of the step")]
    materials: Annotated[list[Material], Field(description="Materials required for this step. Empty if no materials are needed or if source data could not be parsed")] = Field(default_factory=list)
    reference_protocol_ids: Annotated[list[int], Field(description="Protocol IDs referenced by this step. Empty if no references exist or if source data could not be parsed")] = Field(default_factory=list)

    @staticmethod
    def parse(step: str) -> dict:
        description = []
        materials = []
        reference_protocol_ids = []
        material_flag = False
        reference_flag = False
        for line in step.splitlines():
            if material_flag is False and reference_flag is False:
                if line == "[Materials]":
                    material_flag = True
                    reference_flag = False
                elif line == "[Protocol References]":
                    reference_flag = True
                    material_flag = False
                elif len(line) > 0:
                    description.append(line)
            elif material_flag:
                if len(line) == 0 or line[0] != '-':
                    material_flag = False
                    continue
                data = line.split()
                materials.append(Material(
                    name=data[1],
                    quantity=float(data[2]),
                    unit=data[3]
                ))
            elif reference_flag:
                if len(line) == 0 or line[0] != '-':
                    reference_flag = False
                    continue
                data = line.split("[")[1].split("]")[0]
                reference_protocol_ids.append(int(data))
        description = "\n".join(description)
        return {
            "description": description,
            "materials": materials,
            "reference_protocol_ids": reference_protocol_ids
        }

    @classmethod
    def from_api_response(cls, data: dict) -> "ProtocolStep":
        parsed_step = ProtocolStep.parse(data["step"])
        return cls(
            id=data["guid"],
            description=parsed_step["description"],
            materials=parsed_step["materials"],
            reference_protocol_ids=parsed_step["reference_protocol_ids"]
        )

class Protocol(BaseModel):
    id: Annotated[int, Field(description="Unique identifier for the protocol")]
    title: Annotated[str, Field(description="Title of the protocol")]
    description: Annotated[str, Field(description="Description of the protocol")]
    doi: Annotated[str | None, Field(description="DOI of the protocol, if the protocol is private, this will be null")] = None
    url: Annotated[str, Field(description="URL link to the protocol on protocols.io ")]
    created_on: Annotated[datetime, Field(description="Date and time the protocol was created")]
    published_on: Annotated[datetime | None, Field(description="Date and time the protocol was published, if the protocol is private, this will be null")] = None

    @classmethod
    async def from_protocol_id(cls, protocol_id: int) -> "Protocol":
        response = await helpers.access_protocols_io_resource("GET", f"/v4/protocols/{protocol_id}?content_format=markdown")
        protocol = response["payload"]
        return cls(
            id=protocol_id,
            title=protocol["title"],
            description=protocol.get("description") or "",
            doi=protocol.get("doi") or None,
            url=protocol.get("url"),
            created_on=datetime.fromtimestamp(protocol.get("created_on"), tz=timezone.utc),
            published_on=datetime.fromtimestamp(protocol.get("published_on"), tz=timezone.utc) if protocol.get("published_on") else None
        )

class ProtocolSearchResult(BaseModel):
    protocols: Annotated[list[Protocol], Field(description="List of protocols matching the search criteria")]
    current_page: Annotated[int, Field(description="Current page number of the search results, starting from 1")]
    total_pages: Annotated[int, Field(description="Total number of pages available for the search results")]

    @classmethod
    async def from_api_response(cls, data: dict) -> "ProtocolSearchResult":
        protocols = [await Protocol.from_protocol_id(protocol["id"]) for protocol in data["items"]]
        return cls(
            protocols=protocols,
            current_page=data["pagination"]["current_page"],
            total_pages = data["pagination"]["total_pages"]
        )

class ErrorMessage(BaseModel):
    error_message: Annotated[str, Field(description="Error message describing the issue encountered")]

    @classmethod
    def from_string(cls, message: str) -> "ErrorMessage":
        return cls(error_message=message)

@mcp.tool()
async def search_public_protocols(
    keyword: Annotated[str, Field(description="Keyword to search for protocols")],
    page: Annotated[int, Field(description="Page number for pagination, starting from 1")] = 1,
) -> ProtocolSearchResult | ErrorMessage:
    """
    Search for public protocols on protocols.io using a keyword. Results are sorted by protocol popularity and paginated with 3 protocols per page (use the page parameter to navigate, default is 1).

    When searching for reference protocols to create a new protocol:
    - Avoid referencing protocols from before 2015 as they may be outdated.
    - If the found protocols have topics that are not closely related to your needs, ask the user for clearer direction before proceeding.
    - If the found protocols are highly relevant, use get_protocol_steps to examine at least 2 protocols' detailed steps and integrate insights from different approaches to ensure more reliable protocol development.
    """
    page = page - 1 # weird bug in protocols.io API where it returns page 2 if page 1 is requested
    response = await helpers.access_protocols_io_resource("GET", f"/v3/protocols?filter=public&key={keyword}&page_size=3&page_id={page}")
    if response["status_code"] != 0:
        return ErrorMessage.from_string(response["error_message"])
    search_result = await ProtocolSearchResult.from_api_response(response)
    return search_result

@mcp.tool()
async def get_my_protocols() -> list[Protocol] | ErrorMessage:
    """
    Retrieve basic information for all protocols belonging to the current user. To get detailed protocol steps, use get_protocol_steps.
    """
    response_profile = await helpers.access_protocols_io_resource("GET", f"/v3/session/profile", {})
    if response_profile["status_code"] != 0:
        return ErrorMessage.from_string(response_profile["error_message"])
    user = User.from_api_response(response_profile["user"])
    response = await helpers.access_protocols_io_resource("GET", f"/v3/researchers/{user.username}/protocols?filter=user_all")
    if response["status_code"] != 0:
        return ErrorMessage.from_api_response(response["error_message"])
    protocols = [await Protocol.from_protocol_id(protocol["id"]) for protocol in response.get("items")]
    return protocols

@mcp.tool()
async def get_protocol(
    protocol_id: Annotated[int, Field(description="Unique identifier for the protocol")]
) -> Protocol | ErrorMessage:
    """
    Retrieve basic information for a specific protocol by its protocol ID. To get detailed protocol steps, use get_protocol_steps.
    """
    response = await helpers.access_protocols_io_resource("GET", f"/v4/protocols/{protocol_id}")
    if response["status_code"] != 0:
        return ErrorMessage.from_string(response["status_text"])
    protocol = await Protocol.from_protocol_id(response["payload"]["id"])
    return protocol

@mcp.tool()
async def get_protocol_steps(
    protocol_id: Annotated[int, Field(description="Unique identifier for the protocol")]
) -> list[ProtocolStep] | ErrorMessage:
    """
    Retrieve the steps for a specific protocol by its protocol ID.
    """
    response = await helpers.access_protocols_io_resource("GET", f"/v4/protocols/{protocol_id}/steps?content_format=markdown")
    if response["status_code"] != 0:
        return ErrorMessage.from_string(response["status_text"])
    steps = [ProtocolStep.from_api_response(step) for step in response.get("payload", [])]
    return steps

@mcp.tool()
async def create_protocol(
    title: Annotated[str, Field(description="Title of the new protocol")],
    description: Annotated[str, Field(description="Description of the new protocol")],
) -> Protocol | ErrorMessage:
    """
    Create a new protocol with the given title and description.

    Before creating a new protocol, ensure you have searched for at least 2 relevant public protocols using search_public_protocols and reviewed their detailed steps with get_protocol_steps for reference when adding steps.
    """
    response_create_blank_protocol = await helpers.access_protocols_io_resource("POST", f"/v3/protocols/{uuid.uuid4().hex}", {"type_id": 1})
    if response_create_blank_protocol["status_code"] != 0:
        return ErrorMessage.from_string(response_create_blank_protocol["status_text"])
    protocol = await Protocol.from_protocol_id(response_create_blank_protocol["protocol"]["id"])
    data = {"title": title, "description": description}
    response_update_protocol = await helpers.access_protocols_io_resource("PUT", f"/v4/protocols/{protocol.id}", data)
    if response_update_protocol["status_code"] != 0:
        return ErrorMessage.from_string(response_update_protocol["status_text"])
    response_get_protocol = await helpers.access_protocols_io_resource("GET", f"/v4/protocols/{protocol.id}")
    if response_get_protocol["status_code"] != 0:
        return ErrorMessage.from_string(response_get_protocol["status_text"])
    protocol = await Protocol.from_protocol_id(response_get_protocol["payload"]["id"])
    return protocol

@mcp.tool()
async def update_protocol_title(
    protocol_id: Annotated[int, Field(description="Unique identifier for the protocol")],
    title: Annotated[str, Field(description="New title for the protocol")]
) -> Protocol | ErrorMessage:
    """
    Update the title of an existing protocol by its protocol ID.
    """
    data = {"title": title}
    response_update_protocol = await helpers.access_protocols_io_resource("PUT", f"/v4/protocols/{protocol_id}", data)
    if response_update_protocol["status_code"] != 0:
        return ErrorMessage.from_string(response_update_protocol["status_text"])
    response_get_protocol = await helpers.access_protocols_io_resource("GET", f"/v4/protocols/{protocol_id}")
    if response_get_protocol["status_code"] != 0:
        return ErrorMessage.from_string(response_get_protocol["status_text"])
    protocol = await Protocol.from_protocol_id(response_get_protocol["payload"]["id"])
    return protocol

@mcp.tool()
async def update_protocol_description(
    protocol_id: Annotated[int, Field(description="Unique identifier for the protocol")],
    description: Annotated[str, Field(description="New description for the protocol")]
) -> Protocol | ErrorMessage:
    """
    Update the description of an existing protocol by its protocol ID.
    """
    data = {"description": description}
    response_update_protocol = await helpers.access_protocols_io_resource("PUT", f"/v4/protocols/{protocol_id}", data)
    if response_update_protocol["status_code"] != 0:
        return ErrorMessage.from_string(response_update_protocol["status_text"])
    response_get_protocol = await helpers.access_protocols_io_resource("GET", f"/v4/protocols/{protocol_id}")
    if response_get_protocol["status_code"] != 0:
        return ErrorMessage.from_string(response_get_protocol["status_text"])
    protocol = await Protocol.from_protocol_id(response_get_protocol["payload"]["id"])
    return protocol

@mcp.tool()
async def set_protocol_steps(
    protocol_id: Annotated[int, Field(description="Unique identifier for the protocol")],
    steps: Annotated[list[ProtocolStepInput], Field(description="List of steps to set for the protocol")]
) -> list[ProtocolStep] | ErrorMessage:
    """
    Replace the entire steps list of a specific protocol by its protocol ID with a new steps list. The existing steps will be completely overwritten.
    """
    if not steps:
        return ErrorMessage.from_string("At least one step is required to set the protocol steps.")
    # get all existing steps
    response_get_steps = await helpers.access_protocols_io_resource("GET", f"/v4/protocols/{protocol_id}/steps?content_format=markdown")
    if response_get_steps["status_code"] != 0:
        return ErrorMessage.from_string(response_get_steps['status_text'])
    step_existed = [ProtocolStep.from_api_response(step) for step in response_get_steps.get("payload", [])]
    # delete all existing steps
    response_delete_protocol_step = await helpers.access_protocols_io_resource("DELETE", f"/v4/protocols/{protocol_id}/steps", {"steps": [step.id for step in step_existed]})
    if response_delete_protocol_step["status_code"] != 0:
        return ErrorMessage.from_string(response_delete_protocol_step['status_text'])
    # set steps
    data = []
    previous_step_id = None
    for step in steps:
        step_content = await ProtocolStepInput.to_string(step)
        step_data = {
            "guid": uuid.uuid4().hex,
            "previous_guid": previous_step_id,
            "step": step_content
        }
        data.append(step_data)
        previous_step_id = step_data["guid"]
    response_set_steps = await helpers.access_protocols_io_resource("POST", f"/v4/protocols/{protocol_id}/steps", {"steps": data})
    if response_set_steps["status_code"] != 0:
        return ErrorMessage.from_string(response_set_steps['status_text'])
    # get updated steps
    response_get_steps = await helpers.access_protocols_io_resource("GET", f"/v4/protocols/{protocol_id}/steps?content_format=markdown")
    if response_get_steps["status_code"] != 0:
        return ErrorMessage.from_string(response_get_steps['status_text'])
    protocol_steps = [ProtocolStep.from_api_response(step) for step in response_get_steps.get("payload", [])]
    return protocol_steps

@mcp.tool()
async def add_protocol_step(
    protocol_id: Annotated[int, Field(description="Unique identifier for the protocol")],
    step: Annotated[ProtocolStepInput, Field(description="Step to be added to the protocol")]
) -> list[ProtocolStep] | ErrorMessage:
    """
    Add a step to the end of the steps list for a specific protocol by its protocol ID.
    """
    # get all existing steps
    response_get_steps = await helpers.access_protocols_io_resource("GET", f"/v4/protocols/{protocol_id}/steps?content_format=markdown")
    if response_get_steps["status_code"] != 0:
        return ErrorMessage.from_string(response_get_steps["status_text"])
    step_existed = [ProtocolStep.from_api_response(step) for step in response_get_steps.get("payload", [])]
    # get last step ID
    previous_step_id = step_existed[-1].id if step_existed else None
    # add step
    step_content = await ProtocolStepInput.to_string(step)
    step_data = {
        "guid": uuid.uuid4().hex,
        "previous_guid": previous_step_id,
        "step": step_content
    }
    response_add_step = await helpers.access_protocols_io_resource("POST", f"/v4/protocols/{protocol_id}/steps", {"steps": [step_data]})
    if response_add_step["status_code"] != 0:
        return ErrorMessage.from_string(response_add_step["status_text"])
    # get updated steps
    response_get_steps = await helpers.access_protocols_io_resource("GET", f"/v4/protocols/{protocol_id}/steps?content_format=markdown")
    if response_get_steps["status_code"] != 0:
        return ErrorMessage.from_string(response_get_steps["status_text"])
    protocol_steps = [ProtocolStep.from_api_response(step) for step in response_get_steps.get("payload", [])]
    return protocol_steps

@mcp.tool()
async def delete_protocol_step(
    protocol_id: Annotated[int, Field(description="Unique identifier for the protocol")],
    step_id: Annotated[str, Field(description="Unique identifier for the step to be deleted")]
) -> list[ProtocolStep] | ErrorMessage:
    """
    Delete a specific step from a protocol by providing both the protocol ID and step ID.
    """
    response_delete_protocol_step = await helpers.access_protocols_io_resource("DELETE", f"/v4/protocols/{protocol_id}/steps", {"steps": [step_id]})
    if response_delete_protocol_step["status_code"] != 0:
        return ErrorMessage.from_string(response_delete_protocol_step["status_text"])
    response_get_protocol_steps = await helpers.access_protocols_io_resource("GET", f"/v4/protocols/{protocol_id}/steps?content_format=markdown")
    if response_get_protocol_steps["status_code"] != 0:
        return ErrorMessage.from_string(response_get_protocol_steps["status_text"])
    steps = [ProtocolStep.from_api_response(step) for step in response_get_protocol_steps.get("payload", [])]
    return steps