from models.agentic_llm import AgenticLLM
from config.params import EXPERTS_LLM
from config.prompts import experto_estudios_prompt
from tools.vector_search import vector_search_market_studies_tool


market_study_agent = AgenticLLM(
    EXPERTS_LLM,
    tools=[vector_search_market_studies_tool],
    sys_prompt=experto_estudios_prompt,
)
