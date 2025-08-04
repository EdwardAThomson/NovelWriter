"""
Tool interface for NovelWriter agents.

Following Falconer's principles, tools should be:
- Strongly typed: Clear input/output specifications
- Constrained: Small, focused functionality
- Self-describing: Include metadata and examples
- Access-controlled: Scoped to appropriate agents
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json


class ToolAccessLevel(Enum):
    """Access levels for tools."""
    PUBLIC = "public"       # Available to all agents
    RESTRICTED = "restricted"  # Requires specific permissions
    PRIVATE = "private"     # Agent-specific tools


@dataclass
class ToolParameter:
    """Definition of a tool parameter."""
    name: str
    type: str  # "string", "number", "boolean", "object", "array"
    description: str
    required: bool = True
    default: Any = None
    examples: List[Any] = None
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = []


@dataclass
class ToolResult:
    """Result from tool execution."""
    success: bool
    data: Any
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseTool(ABC):
    """
    Abstract base class for all agent tools.
    
    Tools are purpose-built functions that agents can use to accomplish
    specific tasks. Each tool should have a single, well-defined responsibility.
    """
    
    def __init__(self, 
                 name: str, 
                 description: str,
                 access_level: ToolAccessLevel = ToolAccessLevel.PUBLIC):
        self.name = name
        self.description = description
        self.access_level = access_level
        self.parameters = self._define_parameters()
        self.examples = self._define_examples()
    
    @abstractmethod
    def _define_parameters(self) -> List[ToolParameter]:
        """Define the parameters this tool accepts."""
        pass
    
    @abstractmethod
    def _execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass
    
    def _define_examples(self) -> List[Dict[str, Any]]:
        """
        Define usage examples for this tool.
        Override in subclasses to provide specific examples.
        """
        return []
    
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with parameter validation.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            ToolResult with execution outcome
        """
        # Validate parameters
        validation_result = self.validate_parameters(**kwargs)
        if not validation_result.success:
            return validation_result
        
        try:
            # Execute the tool
            import time
            start_time = time.time()
            result = self._execute(**kwargs)
            execution_time = time.time() - start_time
            
            # Add execution time to result
            if result.success:
                result.execution_time = execution_time
                
            return result
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error_message=f"Tool execution failed: {str(e)}"
            )
    
    def validate_parameters(self, **kwargs) -> ToolResult:
        """
        Validate provided parameters against tool specification.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            ToolResult indicating validation success/failure
        """
        errors = []
        
        # Check required parameters
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                errors.append(f"Missing required parameter: {param.name}")
        
        # Check parameter types (basic validation)
        for param_name, param_value in kwargs.items():
            param_def = next((p for p in self.parameters if p.name == param_name), None)
            if param_def is None:
                errors.append(f"Unknown parameter: {param_name}")
                continue
            
            # Basic type checking
            if not self._validate_type(param_value, param_def.type):
                errors.append(f"Parameter {param_name} has invalid type. Expected {param_def.type}")
        
        if errors:
            return ToolResult(
                success=False,
                data=None,
                error_message="; ".join(errors)
            )
        
        return ToolResult(success=True, data=None)
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Basic type validation."""
        type_map = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type is None:
            return True  # Unknown type, skip validation
        
        return isinstance(value, expected_python_type)
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema representation of this tool.
        
        Returns:
            Dictionary containing tool schema for LLM consumption
        """
        return {
            "name": self.name,
            "description": self.description,
            "access_level": self.access_level.value,
            "parameters": {
                "type": "object",
                "properties": {
                    param.name: {
                        "type": param.type,
                        "description": param.description,
                        "examples": param.examples
                    }
                    for param in self.parameters
                },
                "required": [param.name for param in self.parameters if param.required]
            },
            "examples": self.examples
        }
    
    def __str__(self) -> str:
        return f"Tool(name='{self.name}', access_level='{self.access_level.value}')"
    
    def __repr__(self) -> str:
        return self.__str__()


class ToolRegistry:
    """Registry for managing available tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register_tool(self, tool: BaseTool):
        """Register a tool in the registry."""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_available_tools(self, access_level: ToolAccessLevel = None) -> List[BaseTool]:
        """
        Get list of available tools, optionally filtered by access level.
        
        Args:
            access_level: Filter tools by access level
            
        Returns:
            List of available tools
        """
        if access_level is None:
            return list(self._tools.values())
        
        return [tool for tool in self._tools.values() if tool.access_level == access_level]
    
    def get_tools_schema(self, access_level: ToolAccessLevel = None) -> List[Dict[str, Any]]:
        """
        Get schema for all available tools.
        
        Args:
            access_level: Filter tools by access level
            
        Returns:
            List of tool schemas for LLM consumption
        """
        tools = self.get_available_tools(access_level)
        return [tool.get_schema() for tool in tools]
