from core.base_node import LoopingNode
from agents.experto_estudios import market_study_agent


class MarketStudyNodeImpl(LoopingNode):
    """
    Market study analysis node that loops back to itself when continuing
    or goes to supervisor when providing a final response.
    """

    def __init__(self):
        super().__init__(
            agent=market_study_agent,
            node_name="market_study_agent",
            success_route="supervisor",
            max_retries=3,
            fallback_response="RESPUESTA FINAL: He analizado los estudios pero necesito más detalles específicos para proporcionar una respuesta completa. Por favor, reformula tu consulta con más detalles específicos.",
        )

    def _get_agent_display_name(self) -> str:
        """Custom display name for logging"""
        return "Experto Estudios"


# Create the node instance - maintains the same function interface for existing code
market_study_node = MarketStudyNodeImpl()
