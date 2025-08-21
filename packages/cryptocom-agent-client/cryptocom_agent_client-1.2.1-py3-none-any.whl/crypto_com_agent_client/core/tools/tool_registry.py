"""
Tool Registry Module.

This module implements a simplified tool registry that automatically discovers
tools from the built_in_tools list and provides both lazy loading and direct access.
"""

import inspect
from typing import Any, Callable, Dict, List, Optional

from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field


class ToolMetadata(BaseModel):
    """Minimal metadata for a tool without full schema."""
    name: str
    description: str
    category: str = "general"
    parameters: List[str] = Field(default_factory=list)


class ToolRegistry:
    """
    Simplified registry that auto-discovers tools and provides lazy loading.

    This registry automatically discovers all tools from the built_in_tools list
    and extracts metadata without manual registration.
    """

    def __init__(self):
        self._tool_metadata: Dict[str, ToolMetadata] = {}
        self._custom_tools: Dict[str, BaseTool] = {}  # Store custom tools
        self._discover_tools()

    def _discover_tools(self):
        """Auto-discover tools from the built_in_tools list."""
        try:
            # Import the built_in_tools list
            from crypto_com_agent_client.core.tools import built_in_tools

            # Process each tool
            for tool in built_in_tools:
                self._extract_tool_metadata(tool)

            # Add the list_tools to the tool_metadata
            self._tool_metadata["list_tools"] = ToolMetadata(
                name="list_tools",
                description="List all available tools with their descriptions and parameters",
                category="meta",
                parameters=[]
            )

        except ImportError as e:
            print(f"[TOOL_REGISTRY] Warning: Could not import built_in_tools: {e}")

    def _extract_tool_metadata(self, tool: BaseTool):
        """Extract metadata from a tool automatically."""
        # Get tool name - handle StructuredTool objects properly
        if hasattr(tool, 'name'):
            tool_name = tool.name
        else:
            tool_name = getattr(tool, '__name__', 'unknown_tool')

        # Get description
        description = getattr(tool, 'description', None)
        if not description:
            description = getattr(tool, '__doc__', None) or f"Tool: {tool_name}"

        # Extract parameters
        parameters = self._extract_parameters(tool)

        # Categorize tool based on file/module
        category = self._categorize_tool_by_module(tool)

        # Store metadata
        self._tool_metadata[tool_name] = ToolMetadata(
            name=tool_name,
            description=description,
            category=category,
            parameters=parameters
        )

    def _extract_parameters(self, tool: BaseTool) -> List[str]:
        """Extract parameter names from a tool."""
        try:
            # Try to get from args_schema first (for @tool decorated functions)
            if hasattr(tool, 'args_schema') and tool.args_schema:
                return list(tool.args_schema.__fields__.keys())

            # Fallback to function signature inspection
            if hasattr(tool, 'func'):
                sig = inspect.signature(tool.func)
            else:
                sig = inspect.signature(tool)

            # Filter out 'state' parameter as it's injected
            return [name for name in sig.parameters.keys() if name != 'state']

        except Exception as e:
            print(f"Could not extract parameters from {tool}: {e}")
            return []

    def _categorize_tool_by_module(self, tool: BaseTool) -> str:
        """Categorize a tool based on its module/file."""
        try:
            # Get the module name from the tool
            if hasattr(tool, 'func') and hasattr(tool.func, '__module__'):
                module_name = tool.func.__module__
            elif hasattr(tool, '__module__'):
                module_name = tool.__module__
            else:
                return "general"

            # Extract the file name from the module path
            if '.tools.' in module_name:
                return module_name.split('.tools.')[-1]
            else:
                return "general"

        except Exception:
            return "general"

    def get_tool_metadata(self) -> List[ToolMetadata]:
        """Get minimal metadata for all available tools."""
        return list(self._tool_metadata.values())

    def search_tools(self, query: str) -> List[ToolMetadata]:
        """Search tools by name or description."""
        query_lower = query.lower()
        return [
            metadata for metadata in self._tool_metadata.values()
            if query_lower in metadata.name.lower() or query_lower in metadata.description.lower()
        ]

    def load_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Load a specific tool by name."""
        if tool_name == "list_tools":
            return self.list_tools()

        # Check custom tools first
        if tool_name in self._custom_tools:
            return self._custom_tools[tool_name]

        # Load from built_in_tools
        try:
            from crypto_com_agent_client.core.tools import built_in_tools

            for tool in built_in_tools:
                # Handle StructuredTool objects properly
                current_tool_name = getattr(tool, 'name', getattr(tool, '__name__', 'unknown_tool'))
                if current_tool_name == tool_name:
                    return tool

        except ImportError:
            pass

        return None

    def list_tools(self) -> BaseTool:
        """Create a tool for listing all available tools."""
        @tool
        def list_tools_impl() -> str:
            """
            List all available tools with their descriptions and parameters.

            Returns:
                Formatted string listing all available tools
            """
            tools = self.get_tool_metadata()

            if not tools:
                return "No tools available."

            # Group by category
            categories = {}
            for tool in tools:
                if tool.category not in categories:
                    categories[tool.category] = []
                categories[tool.category].append(tool)

            result = [f"Available Tools ({len(tools)} total):\n"]

            for category, category_tools in sorted(categories.items()):
                result.append(f"\n{category.upper()} TOOLS ({len(category_tools)}):")
                for tool in sorted(category_tools, key=lambda x: x.name):
                    result.append(f"  • {tool.name}")
                    result.append(f"    Description: {tool.description}")
                    if tool.parameters:
                        result.append(f"    Parameters: {', '.join(tool.parameters)}")
                    result.append("")

            return "\n".join(result)

        return list_tools_impl

    def register_custom_tools(self, tools: List[BaseTool]) -> None:
        """Register custom tools in the registry."""
        if not tools:
            return

        for tool in tools:
            # Extract metadata
            self._extract_tool_metadata(tool)

            # Store the actual tool for loading
            tool_name = getattr(tool, 'name', getattr(tool, '__name__', 'unknown_tool'))
            self._custom_tools[tool_name] = tool


class ToolDispatcher(BaseTool):
    """
    A tool dispatcher that represents multiple tools with minimal metadata.

    This dispatcher dynamically loads and executes tools when needed.
    """

    name: str = "tool_dispatcher"
    tool_registry: ToolRegistry

    def __init__(self, tool_registry: ToolRegistry, **kwargs):
        """Initialize with a tool registry instance."""
        super().__init__(
            tool_registry=tool_registry,
            description="Dynamic tool dispatcher for blockchain and custom tools",
            **kwargs
        )

    def __getattribute__(self, name):
        """Intercept description access to return dynamic value."""
        if name == "description":
            return self._get_dynamic_description()
        return super().__getattribute__(name)

    def _get_dynamic_description(self) -> str:
        """Generate description dynamically every time it's accessed."""
        base_desc = """Use this tool for ANY blockchain, cryptocurrency, wallet, or DeFi-related queries including:
        - Wallet balance checks and management
        - Token transfers and swaps
        - Transaction lookups and monitoring
        - DeFi protocol interactions
        - Exchange data and pricing
        - Smart contract interactions
        - Block and network data
        - CronosID name resolution

        For all other queries, use the appropriate custom tool."""

        available_tools = ", ".join(sorted(meta.name for meta in self.tool_registry.get_tool_metadata()))
        return f"{base_desc}\n\nAvailable tools: {available_tools}"

    def _run(self, tool_name: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Execute a tool by name with given parameters."""

        if parameters is None:
            parameters = {}

        # Load the actual tool
        actual_tool = self.tool_registry.load_tool(tool_name)
        if not actual_tool:
            available_tools = [meta.name for meta in self.tool_registry.get_tool_metadata()]
            return f"Tool '{tool_name}' not found. Available tools: {', '.join(available_tools)}"

        try:
            # Execute the actual tool
            result = actual_tool.run(parameters)
            return result
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"

    async def _arun(self, tool_name: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Async version of _run."""
        return self._run(tool_name, parameters)
