from typing import Callable, Optional, Dict

from pydantic_ai import Tool

from django_ai_agent.models import Tool as ToolModel
from .toolkit.abstract import AbstractToolkit
from .circuit_breaker import with_circuit_breaker
from ..exceptions import ToolNotFoundError


class ToolService:
    _registered_tools: Dict[str, Callable] = {}

    def __init__(self, agent_model):
        self.agent_model = agent_model

    @classmethod
    def register(cls, name: Optional[str] = None):
        """
        Register a function or AbstractToolkit class as a tool.
        Can be used as a decorator.

        If an AbstractToolkit class is registered, all tools returned by its
        get_tools() method will be registered individually.

        Args:
            name: Optional name for the tool
        """

        def decorator(obj):
            if isinstance(obj, type) and issubclass(obj, AbstractToolkit):
                toolkit_instance = obj()
                toolkit_tools = toolkit_instance.get_tools()

                for tool in toolkit_tools:
                    tool.name = getattr(tool, 'name', getattr(tool, '__name__', 'unknown_tool_name'))
                    if tool.name:
                        cls._registered_tools[tool.name] = tool
            else:
                obj.name = name or getattr(obj, '__name__', str(obj))
                cls._registered_tools[obj.name] = obj

            return obj

        return decorator

    def get_tools(self):
        """
        Get all tools that are available to the agent based on their
        associated tool models.

        Returns:
            List of callable tool functions with circuit breaker applied
        """
        tools = []

        for tool in self.agent_model.tools.filter(is_active=True).all():
            tool_name = tool.name

            if tool_name in self._registered_tools:
                tool_func = self._registered_tools[tool_name]
                circuit_breaker_tool = with_circuit_breaker(tool_func)

                tools.append(Tool(circuit_breaker_tool, max_retries=tool.max_retries, strict=tool.strict))

        return tools

    @classmethod
    def get_tool_function(cls, tool_name):
        """
        Retrieves a tool based on the provided tool name from a collection of tools.
        This method searches for an existing tool by its name and returns its instance
        if found. The functionality assumes the existence of a pre-defined tool
        collection available within the object for querying.

        Args:
            tool_name: The name of the tool to retrieve.

        Returns:
            Tool function with circuit breaker applied
        """
        if tool := cls._registered_tools.get(tool_name):
            return with_circuit_breaker(tool)
        raise ToolNotFoundError()

    @classmethod
    def sync(cls):
        """
        Synchronize all registered tools with the database.
        Creates Tool database models for each registered tool function
        if they don't exist already.

        Returns:
            Tuple of synced tools and inactive tools
        """
        for name, tool_func in cls._registered_tools.items():
            tool_obj = Tool(tool_func)
            description = tool_obj.description
            parameters_schema = tool_obj._base_parameters_json_schema  # noqa

            ToolModel.objects.update_or_create(
                name=name,
                defaults={"description": description, "parameters_schema": parameters_schema, "is_active": True},
            )

        inactive = ToolModel.objects.exclude(name__in=cls._registered_tools.keys()).update(is_active=False)

        return len(cls._registered_tools.keys()), inactive
