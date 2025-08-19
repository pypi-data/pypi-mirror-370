from models.agentic_llm import AgenticLLM
from config.prompts import synthesizer_prompt
from config.params import SUPERVISOR_LLM

synthesizer_agent = AgenticLLM(model=SUPERVISOR_LLM, sys_prompt=synthesizer_prompt)
