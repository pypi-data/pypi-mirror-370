#!/usr/bin/env python3
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from .shell import session_manager
from .config import validate_config_dict


@dataclass
class FunctionResult:
    success: bool
    data: Any
    error: Optional[str] = None
    duration: Optional[float] = None


class FunctionLibrary:
    """Registry of available functions that tools can use"""

    def __init__(self):
        self.functions: Dict[str, Callable] = {}
        self._load_core_functions()

    def _load_core_functions(self):
        """Load built-in function library"""
        self.functions.update(
            {
                "shell_execute": self._shell_execute,
                "shell_interactive": self._shell_interactive,
            }
        )

    async def _shell_execute(
        self, command: str, cwd: Optional[str] = None
    ) -> FunctionResult:
        """Execute shell command"""
        import time

        start = time.time()

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )
            stdout, stderr = await proc.communicate()

            return FunctionResult(
                success=proc.returncode == 0,
                data={
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                    "exit_code": proc.returncode,
                },
                error=stderr.decode() if proc.returncode != 0 else None,
                duration=time.time() - start,
            )
        except Exception as e:
            return FunctionResult(success=False, data=None, error=str(e))

    async def _shell_interactive(
        self,
        command: str,
        session_id: str = "default",
        shell_cmd: str = "bash",
        cwd: Optional[str] = None,
        wait: Union[int, str] = 0,
        custom_prompt: str = "SHELL> ",
        create_new_session: bool = False,
        close_session: bool = False,
    ) -> FunctionResult:
        """
        Execute commands in a persistent interactive shell session

        Args:
            command: Command to execute (ignored if close_session=True)
            session_id: Identifier for the shell session (default: "default")
            shell_cmd: Shell command to use (default: "bash")
            cwd: Working directory for the shell
            timeout: Timeout in seconds for command execution
            custom_prompt: Custom prompt to set for cleaner output
            create_new_session: Force creation of a new session
            close_session: Close the specified session
        """
        import time

        start = time.time()

        # Convert wait to int if it's a string
        if isinstance(wait, str):
            try:
                wait = int(wait)
            except ValueError:
                wait = 0  # Default fallback

        try:
            # Handle session closure
            if close_session:
                result = session_manager.close_session(session_id)
                return FunctionResult(
                    success=result["success"],
                    data=result,
                    error=result.get("error"),
                    duration=time.time() - start,
                )

            # Get or create session
            session = session_manager.get_session(session_id)

            if session is None or create_new_session:
                if create_new_session and session is not None:
                    # Close existing session first
                    session_manager.close_session(session_id)

                # Create new session
                result = session_manager.create_session(
                    session_id=session_id,
                    shell_cmd=shell_cmd,
                    cwd=cwd,
                    custom_prompt=custom_prompt,
                )

                if not result["success"]:
                    error_msg = f"Failed to create session '{session_id}': {result.get('error', 'Unknown error')}"
                    return FunctionResult(
                        success=False,
                        data=result,
                        error=error_msg,
                        duration=time.time() - start,
                    )

                session = session_manager.get_session(session_id)

            # Execute command
            if command:
                result = session_manager.execute_in_session(
                    session_id=session_id, command=command, wait=wait
                )

                if not result["success"]:
                    # Try to get detailed error from result
                    detailed_error = result.get("error") or "Unknown error"
                    if "output" in result and result["output"]:
                        # Include tail of output in error for better debugging
                        output = result["output"]
                        if len(output) > 1000:
                            # Show last 1000 characters for context
                            output_snippet = "..." + output[-1000:]
                        else:
                            output_snippet = output
                        error_msg = f"Command '{command}' failed in session '{session_id}': {detailed_error}. Output tail: {output_snippet}"
                    else:
                        error_msg = f"Command '{command}' failed in session '{session_id}': {detailed_error}"

                    return FunctionResult(
                        success=False,
                        data=result,
                        error=error_msg,
                        duration=result.get("duration", time.time() - start),
                    )

                return FunctionResult(
                    success=result["success"],
                    data=result,
                    error=result.get("error"),
                    duration=result.get("duration", time.time() - start),
                )
            else:
                # Just return session status if no command
                status = session.get_status()
                status["session_id"] = session_id
                return FunctionResult(
                    success=True, data=status, duration=time.time() - start
                )

        except Exception as e:
            return FunctionResult(
                success=False, data=None, error=str(e), duration=time.time() - start
            )


class DynamicToolServer:
    def __init__(self):
        import os

        self.server = Server("fid-mcp")
        self.function_library = FunctionLibrary()
        self.loaded_toolsets: Dict[str, Any] = {}
        # Use PWD to get the actual working directory where the command was invoked
        actual_cwd = Path(os.environ.get("PWD", os.getcwd()))
        self.context = {
            "project_root": str(actual_cwd),
            "home": str(Path.home()),
        }
        self.tools: Dict[str, Dict[str, Any]] = {}

        # Fid knowledge base configuration
        self.fid_config = None
        self.fid_pat = os.environ.get("FID_PAT")

        # Setup handlers
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """Return all dynamically loaded tools plus Fid search"""
            tools = []

            # Always add Fid search tool (will show error if not configured when called)
            tools.append(
                types.Tool(
                    name="search",
                    description="Search the user's Fid knowledge base, which typically contains datasheets, integration manuals, API references, and other technical documentation, particularly for hardware components. ALWAYS try searching Fid first if the user asks about a hardware component, datasheet, manual, or API spec.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query string",
                            }
                        },
                        "required": ["query"],
                    },
                )
            )

            # Add dynamically loaded tools
            for tool_name, tool_def in self.tools.items():
                # Build input schema from parameters
                properties = {}
                required = []

                for param_spec in tool_def.get("toolParams", []):
                    param_name = param_spec["name"]
                    param_type = {"type": "string"}  # Default to string type
                    if "description" in param_spec:
                        param_type["description"] = param_spec["description"]

                    properties[param_name] = param_type

                    if "default" not in param_spec:
                        required.append(param_name)

                input_schema = {
                    "type": "object",
                    "properties": properties,
                }
                if required:
                    input_schema["required"] = required

                tools.append(
                    types.Tool(
                        name=tool_name,
                        description=tool_def["description"],
                        inputSchema=input_schema,
                    )
                )

            return tools

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any] | None
        ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Execute a dynamically loaded tool or Fid search"""

            # Handle Fid search tool
            if name == "search":
                if not self.fid_pat:
                    error_msg = "Personal Access Token (PAT) missing. Please install the Fid MCP server according to these instructions: https://docs.fidlabs.ai/en/latest/connecting-agents.html"
                    return [types.TextContent(type="text", text=f"Error: {error_msg}")]

                if not self.fid_config:
                    error_msg = "No Fid toolkit found in current directory. Download an existing toolkit from your Fid project, or create a new one with these instructions: https://docs.fidlabs.ai/en/latest/toolkits.html"
                    return [types.TextContent(type="text", text=f"Error: {error_msg}")]

                if not arguments or "query" not in arguments:
                    raise ValueError("Query parameter is required")

                try:
                    results = await self._search_fid_knowledge(arguments["query"])
                    return [
                        types.TextContent(
                            type="text", text=json.dumps(results, indent=2)
                        )
                    ]
                except Exception as e:
                    error_msg = f"Search failed: {str(e)}"
                    return [types.TextContent(type="text", text=f"Error: {error_msg}")]

            # Handle dynamic tools
            if name not in self.tools:
                raise ValueError(f"Unknown tool: {name}")

            tool_def = self.tools[name]

            # Apply default parameter values
            final_arguments = {}
            for param_spec in tool_def.get("toolParams", []):
                param_name = param_spec["name"]
                if arguments and param_name in arguments:
                    final_arguments[param_name] = arguments[param_name]
                elif "default" in param_spec:
                    final_arguments[param_name] = param_spec["default"]

            # Initialize execution context
            exec_context = {
                **self.context,
                "params": final_arguments,
                "steps": [],
                "variables": {},
            }

            # Execute each step
            for i, step in enumerate(tool_def["steps"]):
                # Check condition if present
                if "condition" in step:
                    if not self._evaluate_expression(step["condition"], exec_context):
                        continue

                # Resolve parameters based on function type
                if step["function"] == "shell":
                    if "shellParams" in step:
                        step_params = step["shellParams"]
                    else:
                        raise ValueError(f"shell function requires shellParams")
                else:
                    step_params = step.get("params", {})

                resolved_params = self._resolve_params(step_params, exec_context)

                # Map to the actual function call
                if step["function"] == "shell":
                    # Map to shell_interactive function
                    function = self.function_library.functions["shell_interactive"]
                else:
                    function = self.function_library.functions[step["function"]]

                result = await function(**resolved_params)

                # Store result
                exec_context["steps"].append(result)
                exec_context[f"step[{i}]"] = result

                # Capture output if specified
                if "capture_output" in step:
                    exec_context["variables"][step["capture_output"]] = result.data

                # Check assertions
                if "assert" in step and step["assert"]:
                    if not result.data:
                        error_msg = step.get(
                            "error_message", f"Assertion failed at step {i}"
                        )
                        raise ValueError(error_msg)

                # Stop on error
                if not result.success and not step.get("continue_on_error", False):
                    error_msg = f"Step {i} failed - Function: {step['function']}, Error: {result.error or 'Unknown error'}, Params: {resolved_params}"
                    raise ValueError(error_msg)

            # Build output
            output = self._build_output(tool_def.get("output"), exec_context)
            return [types.TextContent(type="text", text=json.dumps(output, indent=2))]

    async def _search_fid_knowledge(self, query: str) -> Dict[str, Any]:
        """Search the Fid knowledge base"""
        import aiohttp
        import time

        start_time = time.time()
        default_k = 6

        # Use the correct projects/{projectId}/search endpoint
        url = f"{self.fid_config['apiBaseUrl']}/projects/{self.fid_config['projectId']}/search"
        headers = {
            "X-API-Key": self.fid_pat,
            "X-Client-Source": "mcp_client",
        }

        payload = {
            "query": query,
            "k": default_k,
            "userId": "",  # Required field, can be empty
            "search_method": "multi_stage",
            "multi_stage_methods": ["full_text", "vector"],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(
                        f"API request failed with status {response.status}: {error_text}"
                    )

                data = await response.json()

                # Log search time
                duration = time.time() - start_time

                if not data.get("results"):
                    return {
                        "results": [],
                        "message": "No search results found",
                        "duration": duration,
                    }

                return {
                    "results": data.get("results", []),
                    "totalCount": data.get("totalCount"),
                    "duration": duration,
                }

    def load_toolset(self, filepath: Path):
        """Load and register tools from a .fidtools or fidtools.json file"""
        with open(filepath, "r") as f:
            toolset = json.load(f)

        # Validate the configuration against the JSON schema
        try:
            validate_config_dict(toolset)
        except ValueError as e:
            raise ValueError(f"Failed to validate toolset '{filepath}': {e}")

        # Extract Fid configuration if present
        if "projectId" in toolset and "apiBaseUrl" in toolset:
            self.fid_config = {
                "projectId": toolset["projectId"],
                "apiBaseUrl": toolset["apiBaseUrl"],
            }

        # Register each tool
        for tool_def in toolset["tools"]:
            self.tools[tool_def["name"]] = tool_def

        self.loaded_toolsets[toolset["name"]] = toolset

    def _resolve_params(
        self, params: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve parameter values with variable substitution"""
        import re

        def resolve_value(value):
            if isinstance(value, str):

                def replacer(match):
                    path = match.group(1).split(".")

                    # Handle simple parameter names by first checking params namespace
                    if len(path) == 1 and path[0] in context.get("params", {}):
                        result = context["params"][path[0]]
                        return str(result) if result is not None else match.group(0)

                    # Handle complex paths
                    result = context
                    for key in path:
                        if key.startswith("step[") and key.endswith("]"):
                            idx = int(key[5:-1])
                            result = context["steps"][idx]
                        else:
                            if isinstance(result, dict):
                                result = result.get(key, None)
                            else:
                                return match.group(0)
                    final_result = str(result) if result is not None else match.group(0)
                    return final_result

                return re.sub(r"\$\{([^}]+)\}", replacer, value)
            elif isinstance(value, dict):
                return {k: resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve_value(v) for v in value]
            return value

        return resolve_value(params)

    def _evaluate_expression(self, expression: str, context: Dict[str, Any]) -> bool:
        """Safely evaluate conditional expressions"""
        resolved = self._resolve_params({"expr": expression}, context)["expr"]

        if resolved.lower() in ("true", "1", "yes"):
            return True
        elif resolved.lower() in ("false", "0", "no", ""):
            return False

        return bool(resolved)

    def _build_output(
        self, output_def: Optional[Dict[str, Any]], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build tool output based on definition"""
        if not output_def:
            if context["steps"]:
                return context["steps"][-1].data
            return {}

        result = {}
        for prop, spec in output_def.get("properties", {}).items():
            if "value" in spec:
                result[prop] = self._resolve_params({"v": spec["value"]}, context)["v"]

        return result

    async def run(self):
        """Run the MCP server"""
        import os
        import sys

        # Use PWD environment variable to get the actual working directory
        # (not uvx's temporary directory)
        working_dir = Path(os.environ.get("PWD", os.getcwd()))

        # Debug logging to file for troubleshooting
        debug_log = Path.home() / "fid_mcp_debug.log"
        with open(debug_log, "a") as f:
            f.write(f"\n--- MCP Server Start ---\n")
            f.write(f"PWD env var: {os.environ.get('PWD')}\n")
            f.write(f"os.getcwd(): {os.getcwd()}\n")
            f.write(f"Using working_dir: {working_dir}\n")

        # Look for .fidtools or fidtools.json file in actual working directory
        config_files = [working_dir / ".fidtools", working_dir / "fidtools.json"]

        config_file = None
        for file_path in config_files:
            if file_path.exists() and file_path.is_file():
                config_file = file_path
                break

        with open(debug_log, "a") as f:
            f.write(
                f"Looking for config files: {', '.join(str(f) for f in config_files)}\n"
            )
            if config_file:
                f.write(f"Found config file: {config_file}\n")
            else:
                f.write("No config file found\n")

        if config_file:
            try:
                self.load_toolset(config_file)
                with open(debug_log, "a") as f:
                    f.write(f"Successfully loaded toolset from {config_file}\n")
                    f.write(f"Loaded {len(self.tools)} tools\n")
            except Exception as e:
                with open(debug_log, "a") as f:
                    f.write(f"ERROR: Failed to load toolset: {e}\n")
                    import traceback

                    f.write(traceback.format_exc())

        # Run the server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="fid-mcp",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


async def async_main():
    server = DynamicToolServer()
    await server.run()


def main():
    """Synchronous entry point for script execution"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
