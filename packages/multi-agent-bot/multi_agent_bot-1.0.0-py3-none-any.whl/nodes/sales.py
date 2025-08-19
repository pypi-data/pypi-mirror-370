from core.base_node import ConditionalNode
from agents.analista_ventas import sales_agent


class SalesNodeImpl(ConditionalNode):
    """
    Sales analysis node that routes to supervisor on "RESPUESTA FINAL" 
    or to text_sql to get more data when continuing.
    """
    
    def __init__(self):
        super().__init__(
            agent=sales_agent,
            node_name="sales_analyst", 
            success_route="supervisor",
            continue_route="text_sql",
            max_retries=3,
            fallback_response="RESPUESTA FINAL: He intentado analizar los datos de ventas solicitados, pero he encontrado dificultades para obtener la información completa. Los datos pueden estar incompletos o la consulta necesita ser más específica. Por favor, reformula tu consulta con detalles como fechas específicas, productos particulares o métricas concretas."
        )
    
    def _get_agent_display_name(self) -> str:
        """Custom display name for logging"""
        return "Analista de Ventas"


# Create the node instance - maintains the same function interface for existing code
sales_node = SalesNodeImpl()
