#!/usr/bin/env python
"""
Modular Super Bot using the Base Bot class

This script creates a comprehensive agent that can:
1. Coordinate research teams for internal market studies (2004-2024) and external web research
2. Synthesize information from multiple sources (internal studies + web data)
3. Provide integrated responses combining historical market research and current market intelligence

Usage:
    python -m main.super_bot "What are the market trends and competitive landscape?"
    python -m main.super_bot --interactive
"""

import sys

from core.base_bot import BaseBot
from nodes.research_team import call_research_team
from nodes.synthesizer import call_synthesizer


class SuperBot(BaseBot):
    """A comprehensive bot that coordinates research teams and synthesis"""

    def __init__(self):
        """Initialize the super bot"""
        # Set up bot-specific configuration
        self.name = "Multi-Agent Research Bot"
        
        # Define team members for this agent
        self.members = {
            "research_team": "Equipo capaz de ejecutar investigaciones en estudios de mercado internos y búsquedas web externas para análisis competitivo.",
            "synthesizer": "Agente con funcionalidad de crear una respuesta para el usuario dada la informacion recompilada. Utilizalo al final para formular un mensaje y despues llama FINISH.",
        }

        # Define the nodes for this agent (supervisor added automatically by BaseBot)
        self.nodes = {
            "research_team": call_research_team,
            "synthesizer": call_synthesizer,
        }
        
        # Initialize the base bot (handles all the common setup)
        super().__init__()
    
    def get_description(self) -> str:
        """Return description for CLI help"""
        return "This bot coordinates comprehensive research combining internal market studies (2004-2024) and external web research with synthesis."


def main():
    """Main entry point"""
    agent = SuperBot()
    return agent.main_cli()


if __name__ == "__main__":
    sys.exit(main())
