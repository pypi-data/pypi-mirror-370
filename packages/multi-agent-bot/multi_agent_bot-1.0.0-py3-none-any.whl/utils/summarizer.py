"""
NLP-based summarization utilities for session management
"""
import logging
from typing import Dict, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from databricks_langchain import ChatDatabricks

logger = logging.getLogger(__name__)


class ResponseSummarizer:
    """Intelligent response summarization using LLM"""
    
    def __init__(self, endpoint: str = "databricks-meta-llama-3-3-70b-instruct"):
        """Initialize with Databricks LLM"""
        self.llm = ChatDatabricks(endpoint=endpoint)
        
        # Summarization prompt template
        self.summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un asistente especializado en crear resúmenes concisos y precisos.
            
Tu tarea es resumir respuestas de chatbots en español en máximo 150 caracteres, manteniendo:
- La información clave y conclusiones principales
- El contexto relevante para futuras consultas
- Un lenguaje claro y directo

IMPORTANTE: 
- Máximo 150 caracteres
- En español
- Sin información redundante
- Enfócate en datos, cifras y conclusiones específicas"""),
            ("human", "Resume esta respuesta del chatbot:\n\n{response}")
        ])
        
        # Conversation summarization prompt
        self.conversation_prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un asistente especializado en resumir conversaciones de negocios.

Crea un resumen de la conversación que capture:
- Temas principales discutidos
- Decisiones o conclusiones alcanzadas  
- Datos importantes mencionados
- Próximos pasos o acciones pendientes

Máximo 300 caracteres. En español."""),
            ("human", "Resumir esta conversación:\n\nConsultas recientes: {queries}\n\nRespuestas principales: {responses}")
        ])
    
    def summarize_response(self, response: str, max_chars: int = 150) -> str:
        """
        Create an intelligent summary of a chatbot response
        
        Args:
            response: The full response text
            max_chars: Maximum characters for summary (default 150)
            
        Returns:
            Intelligent summary of the response
        """
        try:
            # Skip summarization for very short responses
            if len(response) <= max_chars:
                return response
            
            # Use LLM to create summary
            prompt = self.summary_prompt.format_prompt(response=response)
            summary = self.llm.invoke(prompt.to_messages())
            
            summary_text = summary.content.strip()
            
            # Ensure it doesn't exceed max length
            if len(summary_text) > max_chars:
                summary_text = summary_text[:max_chars-3] + "..."
            
            logger.debug(f"Summarized {len(response)} chars to {len(summary_text)} chars")
            return summary_text
            
        except Exception as e:
            logger.error(f"Error summarizing response: {e}")
            # Fallback to truncation
            return response[:max_chars-3] + "..." if len(response) > max_chars else response
    
    def summarize_conversation(self, queries: List[str], responses: List[str], max_chars: int = 300) -> str:
        """
        Create a conversation-level summary
        
        Args:
            queries: List of recent queries
            responses: List of recent response summaries
            max_chars: Maximum characters for summary
            
        Returns:
            Conversation summary
        """
        try:
            if not queries or not responses:
                return ""
            
            # Prepare conversation text
            queries_text = "; ".join(queries[-5:])  # Last 5 queries
            responses_text = "; ".join(responses[-5:])  # Last 5 response summaries
            
            prompt = self.conversation_prompt.format_prompt(
                queries=queries_text,
                responses=responses_text
            )
            
            summary = self.llm.invoke(prompt.to_messages())
            summary_text = summary.content.strip()
            
            # Ensure it doesn't exceed max length
            if len(summary_text) > max_chars:
                summary_text = summary_text[:max_chars-3] + "..."
            
            logger.debug(f"Created conversation summary: {len(summary_text)} chars")
            return summary_text
            
        except Exception as e:
            logger.error(f"Error creating conversation summary: {e}")
            # Fallback to simple concatenation
            fallback = f"Temas: {', '.join(queries[-3:])}"
            return fallback[:max_chars-3] + "..." if len(fallback) > max_chars else fallback


class TopicExtractor:
    """Enhanced topic extraction using NLP"""
    
    def __init__(self, endpoint: str = "databricks-meta-llama-3-3-70b-instruct"):
        """Initialize with Databricks LLM"""
        self.llm = ChatDatabricks(endpoint=endpoint)
        
        self.topic_prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un experto en análisis de negocios para la industria de alimentos.

Extrae los 3 temas de negocio más importantes de este texto, enfocándote en:
- Productos específicos (producta, aceites, harinas, etc.)
- Aspectos comerciales (ventas, precios, márgenes, mercados)
- Análisis estratégicos (tendencias, competencia, oportunidades)
- Operaciones (producción, distribución, calidad)

Responde SOLO con las palabras clave separadas por comas, sin explicaciones.
Ejemplo: "aceite producta, análisis competencia, margen utilidad" """),
            ("human", "Texto: {text}")
        ])
    
    def extract_topics(self, text: str, max_topics: int = 3) -> List[str]:
        """
        Extract key business topics using NLP
        
        Args:
            text: Input text to analyze
            max_topics: Maximum number of topics to extract
            
        Returns:
            List of extracted topics
        """
        try:
            # Fallback keywords for quick matching
            fallback_keywords = [
                'deliproduct', 'deliproducta', 'producta', 'aceite', 'harina',
                'ventas', 'mercado', 'consumidor', 'precio', 'margen',
                'producto', 'marca', 'análisis', 'tendencias', 'competencia',
                'producción', 'calidad', 'distribución'
            ]
            
            # Quick keyword matching first
            text_lower = text.lower()
            found_keywords = [kw for kw in fallback_keywords if kw in text_lower]
            
            # If we have enough keywords, use them
            if len(found_keywords) >= max_topics:
                return found_keywords[:max_topics]
            
            # Use LLM for more sophisticated extraction
            prompt = self.topic_prompt.format_prompt(text=text[:500])  # Limit input length
            result = self.llm.invoke(prompt.to_messages())
            
            topics_text = result.content.strip()
            topics = [topic.strip() for topic in topics_text.split(',')]
            
            # Clean and validate topics
            valid_topics = []
            for topic in topics:
                if topic and len(topic) > 2 and len(topic) < 30:
                    valid_topics.append(topic.lower())
            
            return valid_topics[:max_topics]
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            # Fallback to keyword matching
            text_lower = text.lower()
            fallback_keywords = [
                'deliproduct', 'producta', 'ventas', 'mercado', 'producto', 'análisis'
            ]
            return [kw for kw in fallback_keywords if kw in text_lower][:max_topics]


# Global instances
response_summarizer = ResponseSummarizer()
topic_extractor = TopicExtractor()
