"""
Base Engine Implementation for ProductBot API

This provides a thin API wrapper around BaseBot instances.
BaseEngine leverages BaseBot for all the heavy lifting (session management, query processing, etc.)
and adds API-specific response formatting on top.
"""

from typing import Dict, Any, Optional, Union
from abc import ABC, abstractmethod

from .base_bot import BaseBot
from utils.logger import logger


class BaseEngine(ABC):
    """
    Base class for all API engines.
    This is a thin wrapper around BaseBot that adds API-specific response formatting.
    BaseBot handles all the heavy lifting (session management, query processing, etc.)
    """

    def __init__(self, engine_name: str):
        """
        Initialize the base engine
        
        Args:
            engine_name: Name of the specific engine (e.g., "sales", "search", "super")
        """
        self.engine_name = engine_name
        self.bot = None
        self._initialize_bot()

    @abstractmethod
    def _initialize_bot(self):
        """
        Initialize the specific bot instance - must be implemented by subclasses.
        Should set self.bot to a BaseBot subclass instance.
        """
        pass

    def _get_bot_class_name(self) -> str:
        """
        Return the name of the bot class for logging.
        This can be inferred from the bot instance.
        """
        return self.bot.__class__.__name__ if self.bot else "Unknown"

    def process_query(self, query: str, user_name: str = "user", session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a query through the bot with standardized error handling and response formatting.
        This method is identical across all engines and handles all the common logic.
        
        Args:
            query: The user's query
            user_name: Username for tracking and personalization
            session_id: Optional session ID for conversation continuity
            
        Returns:
            Dict containing the standardized response
        """
        try:
            if not self.bot:
                raise Exception(f"{self._get_bot_class_name()} not initialized")

            logger.info(f"[{self.engine_name}] Processing query from {user_name}: {query}")

            # Process the query using the bot with session management
            result = self.bot.process_query(query, user_name=user_name, session_id=session_id)

            # Format the response consistently
            formatted_response = self._format_response(result)
            
            logger.info(f"[{self.engine_name}] Query processed successfully")
            return formatted_response

        except Exception as e:
            logger.error(f"[{self.engine_name}] Error processing query: {e}")
            return {
                "status": "error",
                "type": f"{self.engine_name}_analysis",
                "message": f"Error processing {self.engine_name} query: {str(e)}",
                "engine": self.engine_name
            }

    def _format_response(self, result: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        """
        Format the bot result for API response with consistent structure.
        This ensures all engines return responses in the same format.
        
        Args:
            result: Raw result from bot
            
        Returns:
            Dict containing formatted response
        """
        try:
            if isinstance(result, dict) and "messages" in result:
                # Extract messages and format them consistently
                messages = result["messages"]
                formatted_messages = []

                for message in messages:
                    if hasattr(message, "content") and hasattr(message, "name"):
                        formatted_messages.append(
                            {"content": message.content, "name": message.name}
                        )
                    elif isinstance(message, dict):
                        formatted_messages.append(message)
                    else:
                        # Fallback for unexpected message format
                        formatted_messages.append(
                            {"content": str(message), "name": "unknown"}
                        )

                return {
                    "status": "success",
                    "type": f"{self.engine_name}_analysis",
                    "messages": formatted_messages,
                    "engine": self.engine_name
                }
            else:
                # Fallback for unexpected result format
                logger.warning(
                    f"[{self.engine_name}] Unexpected result format from {self._get_bot_class_name()}: {type(result)}"
                )
                return {
                    "status": "success", 
                    "type": f"{self.engine_name}_analysis",
                    "result": str(result),
                    "engine": self.engine_name
                }

        except Exception as e:
            logger.error(f"[{self.engine_name}] Error formatting response: {e}")
            return {
                "status": "error",
                "type": f"{self.engine_name}_analysis",
                "message": f"Error formatting response: {str(e)}",
                "engine": self.engine_name
            }

    def health_check(self) -> Dict[str, Any]:
        """
        Check the health status of the engine.
        This method is identical across all engines.
        
        Returns:
            Dict containing health status information
        """
        try:
            if self.bot:
                return {
                    "status": "healthy",
                    "engine": f"{self.engine_name}_engine",
                    "bot_status": "initialized",
                    "bot_type": self._get_bot_class_name(),
                }
            else:
                return {
                    "status": "degraded",
                    "engine": f"{self.engine_name}_engine",
                    "bot_status": "not_initialized",
                    "bot_type": self._get_bot_class_name(),
                }
        except Exception as e:
            logger.error(f"[{self.engine_name}] Health check failed: {e}")
            return {
                "status": "unhealthy", 
                "engine": f"{self.engine_name}_engine", 
                "bot_type": self._get_bot_class_name(),
                "error": str(e)
            }

    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get information about this engine.
        This method is identical across all engines.
        
        Returns:
            Dict containing engine information
        """
        return {
            "engine_name": self.engine_name,
            "bot_type": self._get_bot_class_name(),
            "status": "initialized" if self.bot else "not_initialized",
            "health": self.health_check()["status"]
        }
