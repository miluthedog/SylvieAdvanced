from google.genai import types
from google.genai.types import Tool, FunctionDeclaration
import json


def load_json(file_name: str, title: str): # Load json file
    with open(file_name, "r") as f:
        config_data = json.load(f)
        server_configs = config_data.get(title, [])
        return server_configs

def add_role(role: str, parts) -> types.Content: # Add json "role"
    if isinstance(parts, str):
        parts = [types.Part.from_text(text=parts)]
    return types.Content(role=role, parts=parts)


def convert_mcp_tools_to_gemini(mcp_tools): # Convert MCP tools to Gemini format
    def clean_schema(schema):
        if isinstance(schema, dict):
            cleaned = schema.copy()
            for prop in ["title", "$schema", "additionalProperties", "additional_properties"]: # top-level keys
                cleaned.pop(prop, None)

            dict_keys = ["properties", "definitions"] # dict of schemas
            for key in dict_keys:
                if key in cleaned and isinstance(cleaned[key], dict):
                    cleaned[key] = {k: clean_schema(v) for k, v in cleaned[key].items()}
            list_keys = ["allOf", "anyOf", "oneOf"] # list of schemas
            for key in list_keys:
                if key in cleaned and isinstance(cleaned[key], list):
                    cleaned[key] = [clean_schema(item) for item in cleaned[key]]
            if "items" in cleaned: # single schema
                cleaned["items"] = clean_schema(cleaned["items"])
            return cleaned
        elif isinstance(schema, list):
            return [clean_schema(item) for item in schema]
        return schema

    gemini_tools = []
    for tool in mcp_tools:
        parameters = clean_schema(tool.inputSchema)

        function_declaration = FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters=parameters
        )

        gemini_tool = Tool(function_declarations=[function_declaration])
        gemini_tools.append(gemini_tool)
    return gemini_tools