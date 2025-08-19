#!/usr/bin/env python
"""
Modular Search Agent using the Base Bot class

This script creates a search-focused agent that can:
1.  Analyze user queries
2.  Perform web searches to gather information
3.  Synthesize the search results into a coherent answer

Usage:
    python -m main.search_bot "What are the latest trends in AI?"
    python -m main.search_bot --interactive
"""

import sys

from core.base_bot import BaseBot
from nodes.search import search_node
from nodes.synthesizer import call_synthesizer


class SearchBot(BaseBot):
    """A modular search agent focused on web research"""

    def __init__(self):
        """Initialize the search agent"""
        # Set up bot-specific configuration
        self.name = "Agente de Búsqueda"

        # Define team members for this agent
        self.members = {
            "search_agent": "Experto en investigacion competiva con capacidad de ejecutar encuestas al web",
            "synthesizer": "Agente con funcionalidad de crear una respuesta para el usuario dada la informacion recompilada. Utilizalo al final para formular un mensaje y despues llama FINISH.",
        }

        # Define the nodes for this agent (supervisor added automatically by BaseBot)
        self.nodes = {
            "search_agent": search_node,
            "synthesizer": call_synthesizer,
        }

        # Initialize the base bot (handles all the common setup)
        super().__init__()

    def get_description(self) -> str:
        """Return description for CLI help"""
        return "This agent can perform web searches to answer your questions and gather current information."


def main():
    """Main entry point"""
    agent = SearchBot()
    return agent.main_cli()


if __name__ == "__main__":
    sys.exit(main())
