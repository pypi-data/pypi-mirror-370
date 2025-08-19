from models.agentic_llm import AgenticLLM
from config.params import SUPERVISOR_LLM
from config.prompts import search_prompt
from tools.web_search import web_search_tool

search_agent = AgenticLLM(
    model=SUPERVISOR_LLM, tools=[web_search_tool], sys_prompt=search_prompt
)
