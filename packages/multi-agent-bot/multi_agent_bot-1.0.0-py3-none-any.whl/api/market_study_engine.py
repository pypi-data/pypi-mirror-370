from typing import Dict, Any, Optional

from core.base_engine import BaseEngine
from main.market_study_bot import MarketStudyBot
from utils.logger import logger


class MarketStudyEngine(BaseEngine):
    """
    Market study-focused API engine that provides specialized market analysis.
    Uses the modular MarketStudyBot for consistent architecture.
    """

    def __init__(self):
        """Initialize the Market Study Engine"""
        super().__init__("market_study")

    def _initialize_bot(self):
        """Initialize the MarketStudyBot instance"""
        try:
            self.bot = MarketStudyBot()
        except Exception as e:
            logger.error(f"Failed to initialize MarketStudyBot: {e}")
            raise

    # process_query is inherited from BaseEngine

    def get_market_trends(
        self, period: str = "2020-2024", user_name: str = "user"
    ) -> Dict[str, Any]:
        """
        Get market trends analysis for a specific period

        Args:
            period: Time period to analyze (e.g., "2020-2024", "últimos 5 años")
            user_name: Username for tracking

        Returns:
            Dict containing market trends analysis
        """
        query = f"Analiza las tendencias del mercado de productos genericos para el período {period}, incluyendo cambios en preferencias del consumidor y factores clave del mercado."
        return self.process_query(query, user_name)

    def analyze_consumer_behavior(
        self, segment: str = None, user_name: str = "user"
    ) -> Dict[str, Any]:
        """
        Analyze consumer behavior patterns

        Args:
            segment: Specific consumer segment to analyze (optional)
            user_name: Username for tracking

        Returns:
            Dict containing consumer behavior analysis
        """
        if segment:
            query = f"Proporciona un análisis del comportamiento del consumidor para el segmento {segment} en relación a productos genericos, basándose en estudios de mercado disponibles."
        else:
            query = "Analiza los patrones de comportamiento del consumidor en el mercado de productos genericos, incluyendo motivaciones de compra, frecuencia de consumo y factores de decisión."

        return self.process_query(query, user_name)

    def get_competitive_analysis(
        self, competitor: str = None, user_name: str = "user"
    ) -> Dict[str, Any]:
        """
        Get competitive market analysis

        Args:
            competitor: Specific competitor to analyze (optional)
            user_name: Username for tracking

        Returns:
            Dict containing competitive analysis
        """
        if competitor:
            query = f"Realiza un análisis competitivo comparando CompanyName con {competitor}, basándose en estudios de mercado y posicionamiento."
        else:
            query = "Proporciona un análisis competitivo del mercado de productos genericos, incluyendo la posición de CompanyName frente a la competencia y oportunidades de mercado."

        return self.process_query(query, user_name)

    def get_brand_perception(
        self, brand: str = "CompanyName", user_name: str = "user"
    ) -> Dict[str, Any]:
        """
        Analyze brand perception and positioning

        Args:
            brand: Brand name to analyze (default: "CompanyName")
            user_name: Username for tracking

        Returns:
            Dict containing brand perception analysis
        """
        query = f"Analiza la percepción de marca y posicionamiento de {brand} en el mercado, incluyendo atributos asociados, fortalezas y áreas de oportunidad según estudios de mercado."
        return self.process_query(query, user_name)

    def get_market_segmentation(self, user_name: str = "user") -> Dict[str, Any]:
        """
        Get market segmentation analysis

        Args:
            user_name: Username for tracking

        Returns:
            Dict containing market segmentation analysis
        """
        query = "Proporciona un análisis de segmentación del mercado de productos genericos, identificando los principales segmentos de consumidores, sus características y preferencias."
        return self.process_query(query, user_name)

    # health_check is inherited from BaseEngine


# Create a singleton instance
market_study_engine = MarketStudyEngine()
