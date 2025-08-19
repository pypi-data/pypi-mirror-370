from core.base_node import SimpleNode
from agents.synthesizer import synthesizer_agent


class SynthesizerNodeImpl(SimpleNode):
    """
    Synthesizer node that processes and synthesizes information from other agents.
    This is a SimpleNode that always routes to supervisor after synthesis.
    """
    
    def __init__(self):
        super().__init__(
            agent=synthesizer_agent,
            node_name="synthesizer",
            target_route="supervisor",
            max_retries=2,  # Synthesizer should rarely need retries
            fallback_response="He procesado la información disponible. Basado en los datos analizados, puedo proporcionar una respuesta general, aunque es posible que necesites más detalles específicos para un análisis más profundo."
        )
    
    def _get_agent_display_name(self) -> str:
        """Custom display name for logging"""
        return "Sintetizador"


# Create the node instance - maintains the same function interface for existing code
call_synthesizer = SynthesizerNodeImpl()
