from enum import Enum
from pydantic import BaseModel
from typing import Any, List, TypeVar, Type, cast, Callable
import json
import re
from pathlib import Path


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


class Function(Enum):
    """The type of function to execute"""

    SHELL = "shell"


class ShellParams(BaseModel):
    command: str
    wait: int
    """Wait time in seconds"""

    @staticmethod
    def from_dict(obj: Any) -> 'ShellParams':
        assert isinstance(obj, dict)
        command = from_str(obj.get("command"))
        wait = from_int(obj.get("wait"))
        return ShellParams(command=command, wait=wait)

    def to_dict(self) -> dict:
        result: dict = {}
        result["command"] = from_str(self.command)
        result["wait"] = from_int(self.wait)
        return result


class Step(BaseModel):
    function: Function
    """The type of function to execute"""

    shell_params: ShellParams

    @staticmethod
    def from_dict(obj: Any) -> 'Step':
        assert isinstance(obj, dict)
        function = Function(obj.get("function"))
        shell_params = ShellParams.from_dict(obj.get("shellParams"))
        return Step(function=function, shell_params=shell_params)

    def to_dict(self) -> dict:
        result: dict = {}
        result["function"] = to_enum(Function, self.function)
        result["shellParams"] = to_class(ShellParams, self.shell_params)
        return result


class Param(BaseModel):
    default: str
    name: str

    @staticmethod
    def from_dict(obj: Any) -> 'Param':
        assert isinstance(obj, dict)
        default = from_str(obj.get("default"))
        name = from_str(obj.get("name"))
        return Param(default=default, name=name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["default"] = from_str(self.default)
        result["name"] = from_str(self.name)
        return result


class Tool(BaseModel):
    description: str
    name: str
    steps: List[Step]
    tool_params: List[Param]

    @staticmethod
    def from_dict(obj: Any) -> 'Tool':
        assert isinstance(obj, dict)
        description = from_str(obj.get("description"))
        name = from_str(obj.get("name"))
        steps = from_list(Step.from_dict, obj.get("steps"))
        tool_params = from_list(Param.from_dict, obj.get("toolParams"))
        return Tool(description=description, name=name, steps=steps, tool_params=tool_params)

    def to_dict(self) -> dict:
        result: dict = {}
        result["description"] = from_str(self.description)
        result["name"] = from_str(self.name)
        result["steps"] = from_list(lambda x: to_class(Step, x), self.steps)
        result["toolParams"] = from_list(lambda x: to_class(Param, x), self.tool_params)
        return result


class Version(Enum):
    THE_100 = "1.0.0"


class Coordinate(BaseModel):
    description: str
    name: str
    tools: List[Tool]
    version: Version

    @staticmethod
    def from_dict(obj: Any) -> 'Coordinate':
        assert isinstance(obj, dict)
        description = from_str(obj.get("description"))
        name = from_str(obj.get("name"))
        tools = from_list(Tool.from_dict, obj.get("tools"))
        version = Version(obj.get("version"))
        return Coordinate(description=description, name=name, tools=tools, version=version)

    def to_dict(self) -> dict:
        result: dict = {}
        result["description"] = from_str(self.description)
        result["name"] = from_str(self.name)
        result["tools"] = from_list(lambda x: to_class(Tool, x), self.tools)
        result["version"] = to_enum(Version, self.version)
        return result


def coordinate_from_dict(s: Any) -> Coordinate:
    return Coordinate.from_dict(s)


def coordinate_to_dict(x: Coordinate) -> Any:
    return to_class(Coordinate, x)


def load_and_validate_config(config_path: str) -> Coordinate:
    """Load and validate a fidtools configuration file using Pydantic models"""
    config_path = Path(config_path)
    
    # Load the configuration file
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    # Validate using Pydantic models and additional validation
    validate_config_dict(config_data)
    
    # Convert to Coordinate object
    return coordinate_from_dict(config_data)


def validate_config_dict(config_data: dict) -> None:
    """Validate a configuration dictionary using Pydantic models and check parameter references"""
    # Validate using Pydantic by attempting to create a Coordinate object
    try:
        coordinate_from_dict(config_data)
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {str(e)}")
    
    # Additional validation: check parameter references
    _validate_parameter_references(config_data)


def _validate_parameter_references(config_data: dict) -> None:
    """Validate that all parameter references in shellParams are defined in toolParams"""
    for tool_idx, tool in enumerate(config_data.get("tools", [])):
        tool_name = tool.get("name", f"tool[{tool_idx}]")
        
        # Get defined parameters
        defined_params = set()
        for param in tool.get("toolParams", []):
            defined_params.add(param.get("name"))
        
        # Check each step for parameter references
        for step_idx, step in enumerate(tool.get("steps", [])):
            if step.get("function") == "shell" and "shellParams" in step:
                shell_params = step["shellParams"]
                
                # Check parameter references in command
                if "command" in shell_params:
                    referenced_params = _extract_parameter_references(shell_params["command"])
                    
                    # Check if all referenced parameters are defined
                    undefined_params = referenced_params - defined_params
                    if undefined_params:
                        raise ValueError(
                            f"Tool '{tool_name}' step {step_idx}: "
                            f"shellParams.command references undefined parameters: {sorted(undefined_params)}. "
                            f"Defined parameters: {sorted(defined_params)}"
                        )


def _extract_parameter_references(text: str) -> set:
    """Extract parameter references (${param}) from a text string"""
    if not isinstance(text, str):
        return set()
    
    # Find all ${...} patterns
    pattern = r'\$\{([^}]+)\}'
    matches = re.findall(pattern, text)
    
    # Extract simple parameter names (not complex paths like params.name or step[0].data)
    simple_params = set()
    for match in matches:
        # Only consider simple parameter names (no dots, no brackets)
        if '.' not in match and '[' not in match and ']' not in match:
            simple_params.add(match)
    
    return simple_params
