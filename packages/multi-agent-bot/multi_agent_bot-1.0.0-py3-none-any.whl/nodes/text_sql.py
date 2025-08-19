from core.base_node import SimpleNode
from agents.text_sql import genie_agent


class TextSqlNodeImpl(SimpleNode):
    """
    Text-to-SQL node that converts natural language queries to SQL and executes them.
    This is a SimpleNode that always routes back to sales_analyst after providing data.
    """
    
    def __init__(self):
        super().__init__(
            agent=genie_agent,
            node_name="text_sql",
            target_route="sales_analyst",
            max_retries=5,  # SQL queries might need more attempts
            fallback_response="Error: No se pudieron extraer los datos solicitados debido a problemas técnicos. Por favor, intenta reformular la consulta."
        )
    
    def _get_agent_display_name(self) -> str:
        """Custom display name for logging"""
        return "Text-to-SQL"


# Create the node instance - maintains the same function interface for existing code
data_node = TextSqlNodeImpl()
