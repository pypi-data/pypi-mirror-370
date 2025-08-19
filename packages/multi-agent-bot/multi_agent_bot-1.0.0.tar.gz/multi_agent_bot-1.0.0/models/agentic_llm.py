from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from typing import Optional, List


class AgenticLLM:
    def __init__(
        self,
        model: BaseChatModel,
        tools: Optional[List[Tool]] = None,
        sys_prompt: str = "",
    ):
        if model is None:
            raise ValueError("Model cannot be None. Please ensure the LLM is properly configured.")
        
        self.model = model
        self.tools = tools or []
        self.sys_prompt = sys_prompt
        self.agent = self._build_agent()

    def _build_agent(self) -> Runnable:
        if self.tools:
            return create_react_agent(
                model=self.model,
                tools=self.tools,
                prompt=self.sys_prompt,
            )

        def run(state: dict) -> dict:
            messages = state["messages"]

            visible = (
                [SystemMessage(content=self.sys_prompt)] + messages
                if not any(isinstance(m, SystemMessage) for m in messages)
                else messages
            )

            reply = self.model.invoke(visible)

            return {"messages": messages + [AIMessage(content=reply.content)]}

        return RunnableLambda(run)

    def invoke(self, state: dict) -> dict:
        return self.agent.invoke(state)

    def stream(self, state: dict, config: Optional[dict] = None):
        return self.agent.stream(state, config or {})

    def __call__(self) -> Runnable:
        return self.agent
