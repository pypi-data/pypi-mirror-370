"""
Base Bot Implementation

This eliminates the massive duplication across SuperBot, SalesBot, MarketStudyBot, etc.
All bots inherit from this base class and only define their specific node configurations.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from abc import ABC, abstractmethod

from .base_agent import Agent
from nodes.supervisor import make_supervisor_node
from schemas.state import State
from config.params import SUPERVISOR_LLM
from utils.logger import logger
from utils.session_manager import session_manager
from utils.mlflow_cleanup import cleanup_mlruns
from langchain_core.messages import HumanMessage


class BaseBot(ABC):
    """
    Base class for all bots that eliminates code duplication.
    Subclasses only need to define their specific node configurations.
    """

    def __init__(self):
        """Initialize the bot - subclasses must call this after setting up their config"""
        # These must be set by subclass before calling super().__init__()
        if not hasattr(self, "name"):
            raise ValueError(
                "Subclass must set self.name before calling super().__init__()"
            )
        if not hasattr(self, "members"):
            raise ValueError(
                "Subclass must set self.members before calling super().__init__()"
            )
        if not hasattr(self, "nodes"):
            raise ValueError(
                "Subclass must set self.nodes before calling super().__init__()"
            )

        logger.info(f"Initializing {self.name}...")

        # Create supervisor for this bot
        self.supervisor = make_supervisor_node(llm=SUPERVISOR_LLM, members=self.members)

        # Add supervisor to nodes (bot-specific nodes already set by subclass)
        self.nodes["supervisor"] = self.supervisor

        # Create the agent using super class
        self.agent = Agent(State, self.nodes)

        # Build the graph
        self.graph = self.agent.build_graph()
        logger.info(f"{self.name} initialized successfully")

    def process_query(
        self, query: str, user_name: str = "user", session_id: Optional[str] = None
    ) -> dict:
        """
        Process a query through the bot with session management.
        This method is identical across all bots and handles all the common logic.

        Args:
            query: The query to process
            user_name: Name of the user making the query
            session_id: Current session ID for memory context

        Returns:
            dict: The result from the agent
        """
        if not query:
            logger.warning("Empty query received")
            return None

        logger.info(
            f"Processing query from {user_name} (session: {session_id}): {query}"
        )

        try:
            # Initialize or get existing session
            if not session_id:
                session_id = session_manager.get_or_create_session(user_name)
            else:
                # Use the explicit session_id from the caller (e.g., UI)
                session_id = session_manager.get_or_create_session(
                    user_name, explicit_session_id=session_id
                )

            logger.info(f"Using session_id: {session_id} for user: {user_name}")

            # Fetch session context for the agent prompt
            context_summary = session_manager.get_context_for_agent(
                session_id, self.name
            )
            logger.info(f"Context summary length: {len(context_summary)}")

            # Create user message with context (only add context if it exists)
            if context_summary.strip():
                user_content = (
                    f"CONTEXTO PREVIO:\n{context_summary}\n\nNUEVA CONSULTA: {query}"
                )
                logger.info(
                    f"Added context to query. Full content length: {len(user_content)}"
                )
            else:
                user_content = query
                logger.info("No previous context found, using query as-is")

            user_message = HumanMessage(content=user_content, name=user_name)

            # Process through the agent
            result = self.agent.invoke(
                {
                    "messages": [user_message],
                    "session_id": session_id,
                    "user_id": user_name,
                }
            )

            logger.info("Query processed successfully")

            # Extract final response for logging
            final_response = self._extract_final_response(result)

            # Log interaction
            self._record_interaction(session_id, query, final_response)

            return result

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            return {"error": str(e)}
        finally:
            # Always cleanup MLflow directories after processing
            cleanup_mlruns()

    def _extract_final_response(self, result: dict) -> str:
        """Extract the final response from agent result for logging"""
        final_response = ""
        if "messages" in result and result["messages"]:
            last_message = result["messages"][-1]
            if hasattr(last_message, "content"):
                final_response = last_message.content
            elif isinstance(last_message, dict) and "content" in last_message:
                final_response = last_message["content"]
        return final_response

    def _record_interaction(self, session_id: str, query: str, final_response: str):
        """Record the interaction in session manager"""
        logger.info(
            f"Recording interaction with final_response length: {len(final_response)}"
        )
        try:
            session_manager.record_interaction(
                session_id, query, final_response, self.name
            )
            logger.info("Interaction recorded successfully")
        except Exception as record_e:
            logger.error(f"Failed to record interaction: {record_e}")
            import traceback

            logger.error(f"Record interaction traceback: {traceback.format_exc()}")

    def print_result(self, result: dict):
        """Print the result in a human-readable format"""
        if not result:
            print("\nNo results returned")
            return

        if "error" in result:
            print(f"\nError: {result['error']}")
            return

        if "messages" in result:
            messages = result["messages"]
            print(f"\n===== {self.name} Analysis Results =====\n")
            for i, msg in enumerate(messages):
                content = msg.content if hasattr(msg, "content") else "[No content]"
                name = msg.name if hasattr(msg, "name") else "[No name]"
                print(f"Message {i + 1} (from: {name}):")
                print(f"{content}")
                print("-" * 50)
        else:
            print("\nUnexpected result format")

    @abstractmethod
    def get_description(self) -> str:
        """Return description for CLI help - must be implemented by subclass"""
        pass

    def run_interactive_mode(self):
        """Run the bot in interactive mode - can be overridden by subclass"""
        print("\n" + "=" * 50)
        print(f"  Welcome to the {self.name}")
        print("=" * 50)
        print(f"\n{self.get_description()}")

        try:
            print("\n✓ Bot initialized successfully!")

            while True:
                print("\n" + "-" * 40)
                query = input("\nEnter your query (or 'exit' to quit): ")

                if query.lower() in ("exit", "quit", "bye"):
                    print(f"\nThank you for using {self.name}. Goodbye!")
                    break

                if not query:
                    print("Please enter a query.")
                    continue

                print("\nProcessing your query...")
                result = self.process_query(query)
                self.print_result(result)

        except KeyboardInterrupt:
            print("\n\nSession terminated by user.")
        except Exception as e:
            logger.exception("Unhandled exception in interactive mode")
            print(f"\nAn error occurred: {e}")

    def create_cli_parser(self) -> argparse.ArgumentParser:
        """Create CLI argument parser - can be overridden by subclass"""
        parser = argparse.ArgumentParser(
            description=f"{self.name} - {self.get_description()}"
        )
        parser.add_argument(
            "query",
            nargs="?",
            help="Query to process (if not provided, runs in interactive mode)",
        )
        parser.add_argument(
            "--stream",
            action="store_true",
            help="Run in stream mode to see step-by-step execution",
        )
        parser.add_argument(
            "--interactive", "-i", action="store_true", help="Run in interactive mode"
        )
        return parser

    def process_single_query(self, query: str, stream: bool = False) -> int:
        """Process a single query from command line"""
        try:
            if stream:
                # Use the super class stream method directly
                user_message = HumanMessage(content=query, name="user")
                print(f"\nStreaming analysis for: {query}")
                print("=" * 60)

                for step in self.agent.stream({"messages": [user_message]}):
                    print(step)
                    print("---")
            else:
                result = self.process_query(query)
                self.print_result(result)

            return 0

        except Exception as e:
            logger.exception("Error processing query")
            print(f"Error: {e}")
            return 1

    def main_cli(self) -> int:
        """Main CLI entry point"""
        parser = self.create_cli_parser()
        args = parser.parse_args()

        if args.interactive or not args.query:
            self.run_interactive_mode()
            return 0
        else:
            return self.process_single_query(args.query, args.stream)
