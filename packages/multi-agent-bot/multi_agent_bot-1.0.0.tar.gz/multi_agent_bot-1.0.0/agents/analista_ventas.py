from config.params import SUPERVISOR_LLM
from config.prompts import analista_ventas_prompt
from models.agentic_llm import AgenticLLM

sales_agent = AgenticLLM(model=SUPERVISOR_LLM, sys_prompt=analista_ventas_prompt)
