"""
FIS MCP Server - Python Implementation
Converted from Node.js MCP server for AWS Fault Injection Simulator
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List

import boto3
import mcp.server.stdio
import mcp.types as types
import requests
from mcp.server.fastmcp import FastMCP

# MCP Python SDK imports
from mcp.server.models import InitializationOptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("fis-mcp-server")


# Initialize AWS client
def _get_aws_client():
    """Get AWS FIS client with proper configuration"""
    region = os.environ.get("AWS_REGION", "us-east-1")
    return boto3.client("fis", region_name=region)


client = _get_aws_client()


def _load_config() -> Dict[str, Any]:
    """Load configuration from aws_config.json if it exists"""
    config_path = os.path.join(os.path.dirname(__file__), "aws_config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load config file: {str(e)}")
    return {}


@mcp.tool()
async def create_experiment_template(params: Dict[str, Any]) -> types.CallToolResult:
    """Create a new AWS FIS experiment template"""
    try:
        # Validate and clean actions to remove unsupported parameters
        cleaned_actions = _clean_actions(params["actions"])

        input_params = {
            "description": params["description"],
            "roleArn": params["roleArn"],
            "actions": cleaned_actions,
            "targets": params.get("targets", {}),
            "stopConditions": params["stopConditions"],
        }

        # Add optional parameters
        if "tags" in params:
            input_params["tags"] = params["tags"]

        response = client.create_experiment_template(**input_params)

        result_text = f"Successfully created experiment template:\n{json.dumps(response['experimentTemplate'], indent=2, default=str)}"

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to create experiment template: {str(error)}")


def _clean_actions(actions: Dict[str, Any]) -> Dict[str, Any]:
    """Clean actions to remove unsupported parameters based on action type"""
    cleaned_actions = {}

    # Actions that don't support duration parameter
    no_duration_actions = [
        "aws:ec2:reboot-instances",
        "aws:ec2:stop-instances",
        "aws:ec2:terminate-instances",
        "aws:rds:failover-db-cluster",
        "aws:rds:reboot-db-instances",
    ]

    for action_name, action_config in actions.items():
        cleaned_config = action_config.copy()

        # Remove duration parameter for actions that don't support it
        if action_config.get("actionId") in no_duration_actions:
            if (
                "parameters" in cleaned_config
                and "duration" in cleaned_config["parameters"]
            ):
                logger.warning(
                    f"Removing unsupported 'duration' parameter from action {action_config.get('actionId')}"
                )
                del cleaned_config["parameters"]["duration"]
                # If parameters is now empty, remove it entirely
                if not cleaned_config["parameters"]:
                    del cleaned_config["parameters"]

        cleaned_actions[action_name] = cleaned_config

    return cleaned_actions


@mcp.tool()
async def list_experiment_templates(
    params: Dict[str, Any] = None,
) -> types.CallToolResult:
    """List all AWS FIS experiment templates"""
    try:
        if params is None:
            params = {}

        input_params = {}
        if "maxResults" in params:
            input_params["maxResults"] = params["maxResults"]
        if "nextToken" in params:
            input_params["nextToken"] = params["nextToken"]

        response = client.list_experiment_templates(**input_params)
        templates = response.get("experimentTemplates", [])

        template_list = []
        for template in templates:
            template_list.append(
                {
                    "id": template.get("id"),
                    "description": template.get("description"),
                    "creationTime": template.get("creationTime"),
                    "lastUpdateTime": template.get("lastUpdateTime"),
                    "tags": template.get("tags", {}),
                }
            )

        result_text = f"Found {len(templates)} experiment templates:\n{json.dumps(template_list, indent=2, default=str)}"

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to list experiment templates: {str(error)}")


@mcp.tool()
async def get_experiment_template(template_id: str) -> types.CallToolResult:
    """Get detailed information about a specific experiment template"""
    try:
        response = client.get_experiment_template(id=template_id)

        result_text = f"Experiment template details:\n{json.dumps(response['experimentTemplate'], indent=2, default=str)}"

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to get experiment template: {str(error)}")


@mcp.tool()
async def list_experiments(params: Dict[str, Any] = None) -> types.CallToolResult:
    """List all AWS FIS experiments"""
    try:
        if params is None:
            params = {}

        input_params = {}
        if "maxResults" in params:
            input_params["maxResults"] = params["maxResults"]
        if "nextToken" in params:
            input_params["nextToken"] = params["nextToken"]

        response = client.list_experiments(**input_params)
        experiments = response.get("experiments", [])

        experiment_list = []
        for experiment in experiments:
            experiment_list.append(
                {
                    "id": experiment.get("id"),
                    "experimentTemplateId": experiment.get("experimentTemplateId"),
                    "state": experiment.get("state", {}),
                    "creationTime": experiment.get("creationTime"),
                    "tags": experiment.get("tags", {}),
                }
            )

        result_text = f"Found {len(experiments)} experiments:\n{json.dumps(experiment_list, indent=2, default=str)}"

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to list experiments: {str(error)}")


@mcp.tool()
async def get_experiment(experiment_id: str) -> types.CallToolResult:
    """Get detailed information about a specific experiment"""
    try:
        response = client.get_experiment(id=experiment_id)

        result_text = f"Experiment details:\n{json.dumps(response['experiment'], indent=2, default=str)}"

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to get experiment: {str(error)}")


@mcp.tool()
async def start_experiment(
    template_id: str, tags: Dict[str, str] = None
) -> types.CallToolResult:
    """Start a chaos engineering experiment from a template"""
    try:
        input_params = {"experimentTemplateId": template_id}

        # Add optional tags
        if tags:
            input_params["tags"] = tags

        response = client.start_experiment(**input_params)

        result_text = f"Successfully started experiment:\n{json.dumps(response['experiment'], indent=2, default=str)}"

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to start experiment: {str(error)}")


@mcp.tool()
async def stop_experiment(experiment_id: str) -> types.CallToolResult:
    """Stop a running chaos engineering experiment"""
    try:
        response = client.stop_experiment(id=experiment_id)

        result_text = f"Successfully stopped experiment:\n{json.dumps(response['experiment'], indent=2, default=str)}"

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to stop experiment: {str(error)}")


@mcp.tool()
async def get_aws_resources() -> types.CallToolResult:
    """Get AWS resources available for FIS experiments"""
    try:
        response = requests.get(
            os.environ.get("RESOURCE_SCANNER_URL", ""),
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()

        result_text = f"AWS Resources available for FIS experiments:\n{json.dumps(data, indent=2)}"

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to get AWS resources: {str(error)}")


def handle_list_tools() -> List[types.Tool]:
    """List available tools"""
    logger.info("Handling list_tools request")

    tools = [
        types.Tool(
            name="create_experiment_template",
            description="Create a new AWS FIS experiment template",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Description of the experiment template",
                    },
                    "roleArn": {
                        "type": "string",
                        "description": "IAM role ARN for the experiment",
                    },
                    "actions": {
                        "type": "object",
                        "description": "Actions to perform in the experiment",
                    },
                    "targets": {
                        "type": "object",
                        "description": "Targets for the experiment",
                    },
                    "stopConditions": {
                        "type": "array",
                        "description": "Stop conditions for the experiment",
                    },
                    "tags": {
                        "type": "object",
                        "description": "Tags for the experiment template",
                    },
                },
                "required": [
                    "description",
                    "roleArn",
                    "actions",
                    "stopConditions",
                ],
            },
        ),
        types.Tool(
            name="list_experiment_templates",
            description="List all AWS FIS experiment templates",
            inputSchema={
                "type": "object",
                "properties": {
                    "maxResults": {
                        "type": "number",
                        "description": "Maximum number of results to return",
                    },
                    "nextToken": {
                        "type": "string",
                        "description": "Token for pagination",
                    },
                },
            },
        ),
        types.Tool(
            name="get_experiment_template",
            description="Get detailed information about a specific experiment template",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Experiment template ID",
                    }
                },
                "required": ["id"],
            },
        ),
        types.Tool(
            name="list_experiments",
            description="List all AWS FIS experiments",
            inputSchema={
                "type": "object",
                "properties": {
                    "maxResults": {
                        "type": "number",
                        "description": "Maximum number of results to return",
                    },
                    "nextToken": {
                        "type": "string",
                        "description": "Token for pagination",
                    },
                },
            },
        ),
        types.Tool(
            name="start_experiment",
            description="Start a chaos engineering experiment from a template",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "description": "Experiment template ID to start",
                    },
                    "tags": {
                        "type": "object",
                        "description": "Optional tags for the experiment",
                    },
                },
                "required": ["template_id"],
            },
        ),
        types.Tool(
            name="stop_experiment",
            description="Stop a running chaos engineering experiment",
            inputSchema={
                "type": "object",
                "properties": {
                    "experiment_id": {
                        "type": "string",
                        "description": "Experiment ID to stop",
                    }
                },
                "required": ["experiment_id"],
            },
        ),
        types.Tool(
            name="get_experiment",
            description="Get detailed information about a specific experiment",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Experiment ID"}
                },
                "required": ["id"],
            },
        ),
        types.Tool(
            name="get_aws_resources",
            description="Get AWS resources available for FIS experiments including EC2, ECS, RDS, and Lambda",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific resource types to query (ec2, ecs, rds, lambda). If not specified, all types are queried.",
                    },
                    "include_fis_targets": {
                        "type": "boolean",
                        "description": "Whether to include FIS-compatible target definitions",
                        "default": True,
                    },
                },
            },
        ),
    ]

    # 각 도구가 올바른 형식인지 확인
    for i, tool in enumerate(tools):
        logger.info(f"Tool {i}: {type(tool)} - {getattr(tool, 'name', 'NO_NAME')}")
        if not hasattr(tool, "name"):
            logger.error(f"Tool missing name attribute: {tool}")
            raise ValueError(f"Invalid tool definition: {tool}")

    logger.info(f"Returning {len(tools)} tools")
    return tools


# Tool handler removed - using individual @mcp.tool() decorators instead


def run_server():
    """Run the MCP server"""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
