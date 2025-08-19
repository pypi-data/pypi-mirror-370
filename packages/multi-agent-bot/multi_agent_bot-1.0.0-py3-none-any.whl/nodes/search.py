from core.base_node import LoopingNode
from agents.agente_web import search_agent


class SearchNodeImpl(LoopingNode):
    """
    Web search node that loops back to itself when continuing
    or goes to supervisor when providing a final response.
    """
    
    def __init__(self):
        super().__init__(
            agent=search_agent,
            node_name="search_agent",
            success_route="supervisor",
            max_retries=3,
            fallback_response="RESPUESTA FINAL: He realizado búsquedas web pero necesito más información específica para proporcionar una respuesta completa. Por favor, reformula tu consulta con más detalles."
        )
    
    def _get_agent_display_name(self) -> str:
        """Custom display name for logging"""
        return "Agente Web"


# Create the node instance - maintains the same function interface for existing code
search_node = SearchNodeImpl()
