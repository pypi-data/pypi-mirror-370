from schemas.state import State
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.types import Command
from typing import Literal, Dict
from pydantic import BaseModel
from langgraph.graph import END
from utils.logger import logger


def make_supervisor_node(llm: BaseChatModel, members: Dict[str, str]):
    """Create a simple LLM-based supervisor node for routing between agents"""
    options = ["FINISH"] + [m for m in members.keys()]
    formatted_descriptions = "\n".join(
        f"- {name}: {desc}" for name, desc in members.items()
    )
    system_prompt = (
        "Eres un supervisor inteligente encargado de manejar una conversación entre los"
        f" siguientes trabajadores: \n{formatted_descriptions}\n\n"
        "REGLAS DE ROUTING INTELIGENTE:\n"
        "1. Si el usuario hace un SALUDO simple (hola, hello, buenos días, etc.) o una pregunta muy general, responde con FINISH.\n"
        "2. Si el usuario hace una PREGUNTA ESPECÍFICA, usa el trabajador más apropiado.\n"
        "3. DETECTAR RESPUESTAS INCOMPLETAS: Si un trabajador indica que no tiene información suficiente, datos faltantes, o menciona limitaciones, usa otro trabajador complementario.\n"
        "4. Señales de respuesta incompleta: 'no se resuelve directamente', 'información insuficiente', 'no se proporcionan datos específicos', 'falta información'.\n"
        "5. Solo usa FINISH cuando la pregunta esté completamente respondida.\n\n"
        "IMPORTANTE: No delegates para saludos simples, pero SÍ delega cuando detectes que falta información para responder completamente."
    )

    class Router(BaseModel):
        """Worker to route to next. If no workers needed, route to FINISH."""
        next: Literal[*options]

    def supervisor_node(state: State) -> Command[Literal[*members, "__end__"]]:
        """An LLM-based router."""
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response.next
        logger.info(f"Supervisor: {goto}")
        if goto == "FINISH":
            goto = END

        return Command(goto=goto, update={"next": goto})

    return supervisor_node
