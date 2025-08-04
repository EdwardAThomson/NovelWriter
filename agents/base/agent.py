"""
Base Agent class for NovelWriter agentic system.

This module provides the foundational architecture for all agents in the system,
following the principles from "Don't Build Chatbots — Build Agents With Jobs".
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import json


@dataclass
class AgentMessage:
    """Standard message format for agent communication."""
    sender: str
    recipient: str
    message_type: str  # 'request', 'response', 'notification'
    content: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class AgentResult:
    """Standard result format for agent operations."""
    success: bool
    data: Dict[str, Any]
    messages: List[str]
    metrics: Dict[str, float]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class BaseAgent(ABC):
    """
    Abstract base class for all NovelWriter agents.
    
    Each agent should have a specific job and use purpose-built tools
    to accomplish well-defined tasks with clear success criteria.
    """
    
    def __init__(self, name: str, model: str = "gpt-4o", logger: Optional[logging.Logger] = None):
        self.name = name
        self.model = model
        self.logger = logger or logging.getLogger(f"agent.{name}")
        self.available_tools = []
        self.metrics = {}
        
        self.logger.info(f"Initialized {self.name} agent with model {self.model}")
    
    @abstractmethod
    def get_available_tools(self) -> List[str]:
        """Return list of tools this agent can use."""
        pass
    
    @abstractmethod
    def process_task(self, task_data: Dict[str, Any]) -> AgentResult:
        """
        Process a task using available tools.
        
        Args:
            task_data: Dictionary containing task parameters and context
            
        Returns:
            AgentResult with success status, data, and metrics
        """
        pass
    
    def validate_input(self, task_data: Dict[str, Any]) -> bool:
        """
        Validate input data for the task.
        
        Args:
            task_data: Task parameters to validate
            
        Returns:
            True if input is valid, False otherwise
        """
        required_fields = self.get_required_fields()
        for field in required_fields:
            if field not in task_data:
                self.logger.error(f"Missing required field: {field}")
                return False
        return True
    
    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """Return list of required fields for task_data."""
        pass
    
    def log_metrics(self, metrics: Dict[str, float]):
        """Log performance metrics for this agent."""
        self.metrics.update(metrics)
        self.logger.info(f"Agent metrics: {json.dumps(metrics, indent=2)}")
    
    def send_message(self, recipient: str, message_type: str, content: Dict[str, Any]) -> AgentMessage:
        """
        Create a message to send to another agent or system component.
        
        Args:
            recipient: Target agent or component name
            message_type: Type of message ('request', 'response', 'notification')
            content: Message payload
            
        Returns:
            AgentMessage object
        """
        message = AgentMessage(
            sender=self.name,
            recipient=recipient,
            message_type=message_type,
            content=content
        )
        
        self.logger.debug(f"Sending {message_type} to {recipient}: {content}")
        return message
    
    def handle_error(self, error: Exception, context: str) -> AgentResult:
        """
        Handle errors that occur during task processing.
        
        Args:
            error: The exception that occurred
            context: Description of what was happening when error occurred
            
        Returns:
            AgentResult indicating failure
        """
        error_msg = f"Error in {self.name} during {context}: {str(error)}"
        self.logger.error(error_msg, exc_info=True)
        
        return AgentResult(
            success=False,
            data={},
            messages=[error_msg],
            metrics={"error_count": 1}
        )
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', model='{self.model}')"
    
    def __repr__(self) -> str:
        return self.__str__()
