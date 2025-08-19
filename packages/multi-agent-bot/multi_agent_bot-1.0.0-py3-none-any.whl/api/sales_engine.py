from typing import Dict, Any, Optional

from core.base_engine import BaseEngine
from main.sales_bot import SalesBot
from utils.logger import logger


class SalesEngine(BaseEngine):
    """
    Sales-focused API engine that provides specialized sales analysis and insights.
    Uses the modular SalesBot for consistent architecture.
    """

    def __init__(self):
        """Initialize the Sales Engine"""
        super().__init__("sales")

    def _initialize_bot(self):
        """Initialize the SalesBot instance"""
        try:
            self.bot = SalesBot()
        except Exception as e:
            logger.error(f"Failed to initialize SalesBot: {e}")
            raise

    # process_query is inherited from BaseEngine

    def get_sales_summary(self, user_name: str = "user") -> Dict[str, Any]:
        """
        Get a general sales summary and overview

        Args:
            user_name: Username for tracking

        Returns:
            Dict containing sales summary information
        """
        summary_query = "Proporciona un resumen general de las ventas de CompanyName, incluyendo tendencias recientes y productos principales."
        return self.process_query(summary_query, user_name)

    def analyze_product_performance(
        self, product: str, user_name: str = "user"
    ) -> Dict[str, Any]:
        """
        Analyze performance of a specific product

        Args:
            product: Product name to analyze
            user_name: Username for tracking

        Returns:
            Dict containing product performance analysis
        """
        query = f"Analiza el rendimiento de ventas del producto {product} de CompanyName, incluyendo tendencias y comparaciones."
        return self.process_query(query, user_name)

    def get_regional_analysis(
        self, region: str = None, user_name: str = "user"
    ) -> Dict[str, Any]:
        """
        Get regional sales analysis

        Args:
            region: Specific region to analyze (optional)
            user_name: Username for tracking

        Returns:
            Dict containing regional sales analysis
        """
        if region:
            query = f"Proporciona un análisis de ventas para la región de {region}, incluyendo comparaciones y tendencias."
        else:
            query = "Proporciona un análisis de ventas por regiones, comparando el rendimiento entre diferentes áreas geográficas."

        return self.process_query(query, user_name)

    def get_time_series_analysis(
        self, period: str = "últimos 12 meses", user_name: str = "user"
    ) -> Dict[str, Any]:
        """
        Get time series sales analysis

        Args:
            period: Time period to analyze (e.g., "últimos 6 meses", "2023")
            user_name: Username for tracking

        Returns:
            Dict containing time series analysis
        """
        query = f"Realiza un análisis de series de tiempo de las ventas de CompanyName para el período de {period}, identificando patrones y tendencias."
        return self.process_query(query, user_name)

    # health_check is inherited from BaseEngine


# Create a singleton instance
sales_engine = SalesEngine()
