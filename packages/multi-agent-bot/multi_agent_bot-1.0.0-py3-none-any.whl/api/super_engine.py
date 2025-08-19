from typing import Dict, Any, Optional

from core.base_engine import BaseEngine
from main.super_bot import SuperBot
from utils.logger import logger


class ProductBotEngine(BaseEngine):
    """
    Super engine that manages the comprehensive ProductBot (SuperBot) instances.
    This acts as a wrapper around the SuperBot to provide API-specific functionality.
    """

    def __init__(self):
        """Initialize the ProductBot engine."""
        super().__init__("super")
        # Keep the legacy attribute for backward compatibility
        self.bot_runner = self.bot

    def _initialize_bot(self):
        """Initialize the SuperBot instance"""
        try:
            self.bot = SuperBot()
        except Exception as e:
            logger.error(f"Failed to initialize SuperBot: {e}")
            raise


# Create a singleton instance
engine = ProductBotEngine()
