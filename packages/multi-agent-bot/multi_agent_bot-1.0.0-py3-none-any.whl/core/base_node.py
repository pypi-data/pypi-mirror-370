from abc import ABC, abstractmethod
from typing import Any, Dict
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from schemas.state import State
from utils.logger import logger


class BaseNode(ABC):
    """
    Base class for all LangGraph nodes with common retry logic and routing patterns.
    Provides consistent handling of agent invocation, retry counts, and response processing.
    """
    
    def __init__(self, agent: Any, node_name: str, max_retries: int = 3, fallback_response: str = None):
        self.agent = agent
        self.node_name = node_name
        self.max_retries = max_retries
        self.fallback_response = fallback_response
    
    def __call__(self, state: State) -> Command:
        """
        Main entry point for the node. Handles retry logic, 
        agent invocation, and response processing.
        """
        # 1. Handle retry logic
        retry_counts = self._get_retry_counts(state)
        current_retries = retry_counts.get(self.node_name, 0)
        
        # 2. Check if we've exceeded maximum retries
        if current_retries >= self.max_retries:
            return self._handle_max_retries_exceeded(retry_counts)
        
        # 3. Update retry counter
        updated_retry_counts = self._increment_retry_count(retry_counts, current_retries)
        
        # 4. Invoke the agent
        try:
            result = self.agent.invoke(state)
            response = result["messages"][-1].content
            logger.info(f"{self._get_agent_display_name()} (attempt {current_retries + 1}): {response[:200]}...")
        except Exception as e:
            logger.error(f"Error invoking {self._get_agent_display_name()}: {e}")
            return self._handle_agent_error(retry_counts, str(e))
        
        # 5. Process the response and determine routing
        return self._process_response(response, updated_retry_counts, current_retries)

    def _get_retry_counts(self, state: State) -> Dict[str, int]:
        """Extract and initialize retry counters from state"""
        return state.get("node_retry_counts", {}).copy()

    def _increment_retry_count(self, retry_counts: Dict[str, int], current_retries: int) -> Dict[str, int]:
        """Increment the retry count for this node"""
        updated_counts = retry_counts.copy()
        updated_counts[self.node_name] = current_retries + 1
        return updated_counts

    def _reset_retry_count(self, retry_counts: Dict[str, int]) -> Dict[str, int]:
        """Reset the retry count for this node to 0"""
        reset_counts = retry_counts.copy()
        reset_counts[self.node_name] = 0
        return reset_counts

    def _handle_max_retries_exceeded(self, retry_counts: Dict[str, int]) -> Command:
        """Handle the case when maximum retries have been exceeded"""
        logger.warning(f"{self._get_agent_display_name()} exceeded maximum retries ({self.max_retries}). Using fallback.")
        
        fallback_response = self._get_fallback_response()
        reset_retry_counts = self._reset_retry_count(retry_counts)
        
        return Command(
            update={
                "messages": [HumanMessage(content=fallback_response, name=self.node_name)],
                "node_retry_counts": reset_retry_counts
            },
            goto=self._get_fallback_route(),
        )

    def _handle_agent_error(self, retry_counts: Dict[str, int], error_message: str) -> Command:
        """Handle errors during agent invocation"""
        error_response = f"Error en {self._get_agent_display_name()}: {error_message}"
        reset_retry_counts = self._reset_retry_count(retry_counts)
        
        return Command(
            update={
                "messages": [HumanMessage(content=error_response, name=self.node_name)],
                "node_retry_counts": reset_retry_counts
            },
            goto=self._get_error_route(),
        )

    def _process_response(self, response: str, updated_retry_counts: Dict[str, int], current_retries: int) -> Command:
        """Process the agent response and determine routing"""
        
        # Check if this is a final response
        if self._is_final_response(response):
            logger.info(f"{self._get_agent_display_name()} provided final response")
            final_retry_counts = self._reset_retry_count(updated_retry_counts)
            
            return Command(
                update={
                    "messages": [HumanMessage(content=response, name=self.node_name)],
                    "node_retry_counts": final_retry_counts
                },
                goto=self._get_success_route(),
            )
        else:
            # Continue with updated retry count
            logger.info(f"{self._get_agent_display_name()} continuing (retry {current_retries + 1}/{self.max_retries})")
            
            return Command(
                update={
                    "messages": [HumanMessage(content=response, name=self.node_name)],
                    "node_retry_counts": updated_retry_counts
                },
                goto=self._get_continue_route(),
            )

    # Abstract methods that subclasses must implement

    @abstractmethod
    def _get_success_route(self) -> str:
        """Return the route to take when the agent provides a final response"""
        pass

    @abstractmethod
    def _get_continue_route(self) -> str:
        """Return the route to take when the agent needs to continue processing"""
        pass

    @abstractmethod
    def _get_fallback_route(self) -> str:
        """Return the route to take when max retries are exceeded"""
        pass

    # Methods with default implementations that can be overridden

    def _get_error_route(self) -> str:
        """Return the route to take when there's an agent error (default: fallback route)"""
        return self._get_fallback_route()

    def _is_final_response(self, response: str) -> bool:
        """Check if the response indicates completion (default: check for 'RESPUESTA FINAL')"""
        return "RESPUESTA FINAL" in response

    def _get_fallback_response(self) -> str:
        """Get the fallback response when max retries are exceeded"""
        if self.fallback_response:
            return self.fallback_response
        return f"RESPUESTA FINAL: He intentado procesar la solicitud con {self._get_agent_display_name()}, pero he encontrado dificultades. Por favor, reformula tu consulta o intenta más tarde."

    def _get_agent_display_name(self) -> str:
        """Get a human-readable name for logging (default: node_name)"""
        return self.node_name.replace("_", " ").title()


class SimpleNode(BaseNode):
    """
    A simple node implementation for nodes that ALWAYS go to the same route
    regardless of response content (like synthesizer -> supervisor, text_sql -> sales_analyst).
    These nodes don't check for "RESPUESTA FINAL" - they always route the same way.
    """
    
    def __init__(self, agent: Any, node_name: str, target_route: str, max_retries: int = 3, fallback_response: str = None):
        super().__init__(agent, node_name, max_retries, fallback_response)
        self.target_route = target_route
    
    def _get_success_route(self) -> str:
        return self.target_route
    
    def _get_continue_route(self) -> str:
        return self.target_route
    
    def _get_fallback_route(self) -> str:
        return self.target_route
        
    def _is_final_response(self, response: str) -> bool:
        """Simple nodes don't check for final response - they always continue to target"""
        return False  # Always "continue" (which goes to target_route)


class ConditionalNode(BaseNode):
    """
    A conditional node implementation for nodes that have different routes
    for success vs. continue (like sales_node -> supervisor vs. text_sql).
    """
    
    def __init__(self, agent: Any, node_name: str, success_route: str, continue_route: str, 
                 fallback_route: str = None, max_retries: int = 3, fallback_response: str = None):
        super().__init__(agent, node_name, max_retries, fallback_response)
        self.success_route = success_route
        self.continue_route = continue_route
        self.fallback_route = fallback_route or success_route
    
    def _get_success_route(self) -> str:
        return self.success_route
    
    def _get_continue_route(self) -> str:
        return self.continue_route
    
    def _get_fallback_route(self) -> str:
        return self.fallback_route


class LoopingNode(BaseNode):
    """
    A looping node implementation for nodes that loop back to themselves
    when they don't have a final response (like market_study_node, search_node).
    These check for "RESPUESTA FINAL" and either go to supervisor or loop back to themselves.
    """
    
    def __init__(self, agent: Any, node_name: str, success_route: str = "supervisor", max_retries: int = 3, fallback_response: str = None):
        super().__init__(agent, node_name, max_retries, fallback_response)
        self.success_route = success_route
    
    def _get_success_route(self) -> str:
        return self.success_route
    
    def _get_continue_route(self) -> str:
        # Looping nodes go back to themselves when continuing
        return self.node_name
    
    def _get_fallback_route(self) -> str:
        return self.success_route
