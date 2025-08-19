from core.base_node import SimpleNode
from core.base_agent import Agent
from nodes.supervisor import make_supervisor_node
from nodes.market_study import market_study_node
from nodes.search import search_node
from config.params import SUPERVISOR_LLM
from schemas.state import State


# Research team configuration
equipo_investigacion = {
    "market_study_agent": (
        "Experto en estudios de mercado históricos de CompanyName (2004-2024). Usa para análisis, percepciones, estrategias "
        "y contexto interno de CompanyName y competidores cuando sea relevante para la consulta."
    ),
    "search_agent": (
        "Especialista en búsqueda web externa. Usa cuando necesites: precios actuales, información reciente de competidores, "
        "análisis de redes sociales en tiempo real, datos no disponibles internamente, o cuando el usuario solicite contexto externo. "
        "OBLIGATORIO: Usa también cuando market_study_agent indique que no tiene datos suficientes para responder completamente."
    ),
}

# Create internal supervisor for the research team
supervisor = make_supervisor_node(SUPERVISOR_LLM, equipo_investigacion)

# Internal research team nodes
nodes = {
    "supervisor": supervisor,
    "market_study_agent": market_study_node,
    "search_agent": search_node,
}

# Create the composite research team agent
research_team = Agent(State, nodes)


class ResearchTeamNodeImpl(SimpleNode):
    """
    Research team node that wraps a composite Agent containing market study and search agents.
    This is a SimpleNode that always routes to supervisor after completing internal research.
    """

    def __init__(self):
        super().__init__(
            agent=research_team,
            node_name="research_team",
            target_route="supervisor",
            max_retries=5,  # Research team needs more coordination attempts
            fallback_response="El equipo de investigación ha analizado los datos, pero no pudo completar la tare. Por favor, brinda una encuesta mas especifica.",
        )

    def _get_agent_display_name(self) -> str:
        """Custom display name for logging"""
        return "Supervisor Investigacion"


# Create the node instance - maintains the same function interface for existing code
call_research_team = ResearchTeamNodeImpl()
