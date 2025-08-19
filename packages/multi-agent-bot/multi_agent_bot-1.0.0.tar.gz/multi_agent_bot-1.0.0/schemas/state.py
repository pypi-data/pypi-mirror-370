from langgraph.graph import MessagesState
from typing import Optional, Dict


class State(MessagesState):
    next: str
    # Minimal session tracking - actual memory stored externally
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    # Loop detection counters to prevent infinite loops
    node_retry_counts: Optional[Dict[str, int]] = None
