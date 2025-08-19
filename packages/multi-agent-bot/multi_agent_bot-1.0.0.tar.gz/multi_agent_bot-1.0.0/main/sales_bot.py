#!/usr/bin/env python
"""
Modular Sales Agent using the Base Bot class

This script creates a sales-focused agent that can:
1. Analyze sales queries
2. Extract data from SQL databases via genie agent
3. Provide final sales analysis

Usage:
    python -m main.sales_bot "What were the sales figures for 2023?"
    python -m main.sales_bot --interactive
"""

import sys

from core.base_bot import BaseBot
from nodes.sales import sales_node
from nodes.text_sql import data_node
from nodes.synthesizer import call_synthesizer


class SalesBot(BaseBot):
    """A modular sales agent focused on sales data analysis"""

    def __init__(self):
        """Initialize the sales agent"""
        # Set up bot-specific configuration
        self.name = "Agente de Ventas"
        
        # Define team members for this agent
        self.members = {
            "sales_analyst": "Analista de ventas, capaz de extraer datos de ventas a clientes directos nacionales e internacionales (exportacion)",
            "synthesizer": "Agente con funcionalidad de crear una respuesta para el usuario dada la informacion recompilada. Utilizalo al final para formular un mensaje y despues llama FINISH.",
        }

        # Define the nodes for this agent (supervisor added automatically by BaseBot)
        self.nodes = {
            "sales_analyst": sales_node,
            "text_sql": data_node,
            "synthesizer": call_synthesizer,
        }
        
        # Initialize the base bot (handles all the common setup)
        super().__init__()
    
    def get_description(self) -> str:
        """Return description for CLI help"""
        return "This agent specializes in sales data analysis and queries. It can extract and analyze sales data from your database."


def main():
    """Main entry point"""
    agent = SalesBot()
    return agent.main_cli()


if __name__ == "__main__":
    sys.exit(main())
