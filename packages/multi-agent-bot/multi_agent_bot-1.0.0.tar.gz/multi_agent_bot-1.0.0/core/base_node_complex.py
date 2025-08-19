"""
Base Node Implementation for ProductBot LangGraph Nodes

This eliminates the massive duplication across all nodes by providing common retry logic,
state management, agent invocation patterns, and response processing.
All nodes inherit from this base class and only define their specific routing logic.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, Union
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from schemas.state import State
from utils.logger import logger
from utils.session_manager import session_manager


class BaseNode(ABC):
    """
    Base class for all LangGraph nodes that eliminates code duplication.
    Handles retry logic, state management, agent invocation, and response processing.
    Subclasses only need to define their specific routing and agent configuration.
    """

    def __init__(self, agent: Any, node_name: str, max_retries: int = 3):
        """
        Initialize the base node
        
        Args:
            agent: The LangChain agent to invoke
            node_name: Name of this node for logging and retry tracking
            max_retries: Maximum number of retries before fallback (default: 3)
        """
        self.agent = agent
        self.node_name = node_name
        self.max_retries = max_retries

    def __call__(self, state: State) -> Command:
        """
        Main execution method that handles all common node logic.
        This method is identical across all nodes and handles retry logic, 
        agent invocation, and response processing.
        
        Args:
            state: Current LangGraph state
            
        Returns:
            Command with updated state and routing decision
        """
        # 1. Handle retry logic
        retry_counts = self._get_retry_counts(state)
        current_retries = retry_counts.get(self.node_name, 0)
        
        # 2. Check if we've exceeded maximum retries
        if current_retries >= self.max_retries:
            return self._handle_max_retries_exceeded(retry_counts, state)
        
        # 3. Update retry counter
        updated_retry_counts = self._increment_retry_count(retry_counts, current_retries)
        
        # 4. Invoke the agent
        try:
            result = self.agent.invoke(state)
            response = result["messages"][-1].content
            logger.info(f"{self._get_agent_display_name()} (attempt {current_retries + 1}): {response[:200]}...")
        except Exception as e:
            logger.error(f"Error invoking {self._get_agent_display_name()}: {e}")
            return self._handle_agent_error(retry_counts, str(e))
        
        # 5. Process the response and determine routing
        return self._process_response(response, updated_retry_counts, current_retries)

    def _get_retry_counts(self, state: State) -> Dict[str, int]:
        """Extract and initialize retry counters from state"""
        if state.get("node_retry_counts") is None:
            return {}
        else:
            return state["node_retry_counts"].copy()

    def _increment_retry_count(self, retry_counts: Dict[str, int], current_retries: int) -> Dict[str, int]:
        """Increment the retry count for this node"""
        updated_counts = retry_counts.copy()
        updated_counts[self.node_name] = current_retries + 1
        return updated_counts

    def _reset_retry_count(self, retry_counts: Dict[str, int]) -> Dict[str, int]:
        """Reset the retry count for this node to 0"""
        reset_counts = retry_counts.copy()
        reset_counts[self.node_name] = 0
        return reset_counts

    def _handle_max_retries_exceeded(self, retry_counts: Dict[str, int], state: State = None) -> Command:
        """Handle the case when maximum retries have been exceeded with intelligent context sharing"""
        logger.warning(f"{self._get_agent_display_name()} exceeded maximum retries ({self.max_retries}). Providing intelligent fallback.")
        
        # Extract context information for supervisor
        context_info = self._extract_failure_context(state)
        
        # Create intelligent fallback response with context
        fallback_response = self._get_intelligent_fallback_response(context_info)
        reset_retry_counts = self._reset_retry_count(retry_counts)
        
        # Record the failure in session memory for future reference
        self._record_agent_failure(state, context_info)
        
        return Command(
            update={
                "messages": [HumanMessage(content=fallback_response, name=self.node_name)],
                "node_retry_counts": reset_retry_counts,
                "agent_failure_context": {  # Add failure context for supervisor
                    "failed_agent": self.node_name,
                    "display_name": self._get_agent_display_name(),
                    "max_retries_reached": True,
                    "context_info": context_info,
                    "suggested_alternatives": self._get_alternative_approaches(),
                    "failure_type": "max_retries_exceeded"
                }
            },
            goto=self._get_fallback_route(),
        )

    def _handle_agent_error(self, retry_counts: Dict[str, int], error_message: str) -> Command:
        """Handle errors during agent invocation"""
        error_response = f"Error en {self._get_agent_display_name()}: {error_message}"
        reset_retry_counts = self._reset_retry_count(retry_counts)
        
        return Command(
            update={
                "messages": [HumanMessage(content=error_response, name=self.node_name)],
                "node_retry_counts": reset_retry_counts
            },
            goto=self._get_error_route(),
        )

    def _process_response(self, response: str, updated_retry_counts: Dict[str, int], current_retries: int) -> Command:
        """Process the agent response and determine routing"""
        
        # Check if this is a final response
        if self._is_final_response(response):
            logger.info(f"{self._get_agent_display_name()} provided final response")
            final_retry_counts = self._reset_retry_count(updated_retry_counts)
            
            return Command(
                update={
                    "messages": [HumanMessage(content=response, name=self.node_name)],
                    "node_retry_counts": final_retry_counts
                },
                goto=self._get_success_route(),
            )
        else:
            # Continue with updated retry count
            logger.info(f"{self._get_agent_display_name()} continuing (retry {current_retries + 1}/{self.max_retries})")
            
            return Command(
                update={
                    "messages": [HumanMessage(content=response, name=self.node_name)],
                    "node_retry_counts": updated_retry_counts
                },
                goto=self._get_continue_route(),
            )

    # Abstract methods that subclasses must implement

    @abstractmethod
    def _get_success_route(self) -> str:
        """Return the route to take when the agent provides a final response"""
        pass

    @abstractmethod
    def _get_continue_route(self) -> str:
        """Return the route to take when the agent needs to continue processing"""
        pass

    @abstractmethod
    def _get_fallback_route(self) -> str:
        """Return the route to take when max retries are exceeded"""
        pass

    # Methods with default implementations that can be overridden

    def _get_error_route(self) -> str:
        """Return the route to take when there's an agent error (default: fallback route)"""
        return self._get_fallback_route()

    def _is_final_response(self, response: str) -> bool:
        """Check if the response indicates completion (default: check for 'RESPUESTA FINAL')"""
        return "RESPUESTA FINAL" in response

    def _get_fallback_response(self) -> str:
        """Get the fallback response when max retries are exceeded"""
        return f"He intentado procesar la solicitud con {self._get_agent_display_name()}, pero he encontrado dificultades. Por favor, reformula tu consulta o intenta más tarde."

    def _get_agent_display_name(self) -> str:
        """Get a human-readable name for logging (default: node_name)"""
        return self.node_name.replace("_", " ").title()
    
    # Intelligent Context Methods
    
    def _extract_failure_context(self, state: State) -> Dict[str, Any]:
        """Extract detailed failure context including data gathered and failure nature"""
        context = {
            "agent_name": self.node_name,
            "display_name": self._get_agent_display_name(),
            "attempt_count": self.max_retries,
        }
        
        if not state:
            return context
            
        messages = state.get("messages", [])
        
        # Extract the original user query
        user_query = ""
        for msg in messages:
            if hasattr(msg, "name") and getattr(msg, "name", "") in ["user", "human"]:
                user_query = getattr(msg, "content", "")
                break
        
        context["original_query"] = user_query
        
        # Analyze what data was actually gathered in failed attempts
        failed_attempts_data = []
        for msg in messages:
            if hasattr(msg, "name") and getattr(msg, "name", "") == self.node_name:
                attempt_content = getattr(msg, "content", "")
                
                # Extract actual data/results from the attempt
                attempt_analysis = {
                    "content": attempt_content,
                    "had_data": self._extract_data_from_response(attempt_content),
                    "failure_indicators": self._identify_failure_indicators(attempt_content),
                    "partial_results": self._extract_partial_results(attempt_content),
                    "data_quality": self._assess_data_quality(attempt_content),
                    "completion_level": self._assess_completion_level(attempt_content)
                }
                failed_attempts_data.append(attempt_analysis)
        
        context["failed_attempts_analysis"] = failed_attempts_data
        
        # Determine the specific nature of the failure
        context["failure_analysis"] = {
            "failure_type": self._classify_failure_type(failed_attempts_data, user_query),
            "data_issues": self._identify_data_issues(failed_attempts_data),
            "query_problems": self._identify_query_problems(user_query, failed_attempts_data),
            "agent_limitations": self._identify_agent_limitations(failed_attempts_data),
            "suggested_data_sources": self._suggest_alternative_data_sources(user_query, failed_attempts_data)
        }
        
        # Extract any partial data that was successfully gathered
        context["gathered_data"] = self._consolidate_partial_data(failed_attempts_data)
        
        # Session context
        session_id = state.get("session_id")
        if session_id:
            context["session_id"] = session_id
            try:
                session_context = session_manager.get_context_for_agent(session_id, self.node_name)
                if session_context:
                    context["session_context"] = session_context[:200]
            except Exception as e:
                logger.error(f"Error getting session context: {e}")
        
        return context
    
    def _get_intelligent_fallback_response(self, context_info: Dict[str, Any]) -> str:
        """Create an intelligent fallback response with context information"""
        base_response = f"RESPUESTA FINAL: He intentado procesar tu consulta usando {self._get_agent_display_name()}"
        
        # Add context-aware details
        context_details = []
        
        if "session_context" in context_info:
            context_details.append("basándome en nuestro historial de conversación")
        
        if "recent_messages" in context_info and context_info["recent_messages"]:
            context_details.append("considerando la información previamente discutida")
        
        # Add specific failure reason based on agent type
        failure_reason = self._get_agent_specific_failure_reason()
        if failure_reason:
            context_details.append(failure_reason)
        
        context_text = ", ".join(context_details) if context_details else ""
        if context_text:
            base_response += f" {context_text},"
        
        base_response += f" pero he encontrado dificultades después de {self.max_retries} intentos. "
        base_response += "El supervisor puede ayudarte a reformular la consulta o explorar enfoques alternativos."
        
        return base_response
    
    def _get_agent_specific_failure_reason(self) -> str:
        """Get agent-specific failure reason - can be overridden by subclasses"""
        agent_reasons = {
            "sales_analyst": "analizando los datos de ventas",
            "market_study_agent": "investigando los estudios de mercado",
            "search_agent": "realizando búsquedas web",
            "text_sql": "extrayendo datos de la base de datos",
            "synthesizer": "sintetizando la información"
        }
        return agent_reasons.get(self.node_name, "procesando tu solicitud")
    
    def _get_alternative_approaches(self) -> List[str]:
        """Suggest alternative approaches - can be overridden by subclasses"""
        general_alternatives = [
            "Reformular la consulta con más detalles específicos",
            "Dividir la consulta en partes más pequeñas",
            "Usar un enfoque diferente para obtener la información"
        ]
        
        # Agent-specific alternatives
        agent_alternatives = {
            "sales_analyst": [
                "Especificar un período de tiempo más concreto para el análisis",
                "Enfocar la consulta en productos o regiones específicas",
                "Solicitar métricas de ventas más básicas primero"
            ],
            "market_study_agent": [
                "Solicitar estudios sobre un mercado o segmento específico",
                "Preguntar sobre tendencias en períodos más recientes",
                "Enfocar en aspectos particulares del comportamiento del consumidor"
            ],
            "search_agent": [
                "Usar términos de búsqueda más específicos",
                "Solicitar información sobre temas más concretos",
                "Preguntar sobre industrias o mercados particulares"
            ]
        }
        
        specific_alternatives = agent_alternatives.get(self.node_name, [])
        return specific_alternatives + general_alternatives
    
    def _record_agent_failure(self, state: State, context_info: Dict[str, Any]):
        """Record agent failure in session memory for future reference"""
        if not state or "session_id" not in state:
            return
        
        session_id = state["session_id"]
        
        try:
            session = session_manager.get_session(session_id)
            if session:
                # Add failure info to agent memory
                failure_memory = {
                    "type": "agent_failure",
                    "agent": self.node_name,
                    "display_name": self._get_agent_display_name(),
                    "max_retries_reached": True,
                    "context_summary": context_info.get("session_context", "")[:100],
                    "suggested_alternatives": self._get_alternative_approaches()[:2],  # Top 2 alternatives
                    "failure_analysis": context_info.get("failure_analysis", {}),
                    "gathered_data": context_info.get("gathered_data", {})
                }
                
                session.add_agent_memory(self.node_name, failure_memory)
                logger.info(f"Recorded failure for {self.node_name} in session {session_id[:8]}...")
        except Exception as e:
            logger.error(f"Error recording agent failure: {e}")
    
    # Data Analysis Helper Methods
    
    def _extract_data_from_response(self, response: str) -> Dict[str, Any]:
        """Extract actual data elements from agent response"""
        data = {
            "has_numbers": bool(__import__('re').search(r'\d+', response)),
            "has_tables": '|' in response or '\n' in response and '  ' in response,
            "has_dates": bool(__import__('re').search(r'\d{4}|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre', response.lower())),
            "has_currency": '$' in response or 'USD' in response or 'dólares' in response or 'millones' in response,
            "has_percentages": '%' in response or 'porciento' in response,
            "content_length": len(response),
            "seems_truncated": response.endswith('...') or len(response) > 1000
        }
        return data
    
    def _identify_failure_indicators(self, response: str) -> List[str]:
        """Identify specific indicators of why the response failed"""
        indicators = []
        response_lower = response.lower()
        
        if "no se encontr" in response_lower or "no hay datos" in response_lower:
            indicators.append("no_data_found")
        if "error" in response_lower:
            indicators.append("error_occurred")
        if "no puedo" in response_lower or "no es posible" in response_lower:
            indicators.append("agent_limitation")
        if "necesito más información" in response_lower or "más específico" in response_lower:
            indicators.append("insufficient_query_detail")
        if "timeout" in response_lower or "tiempo agotado" in response_lower:
            indicators.append("timeout_occurred")
        if len(response) < 50:
            indicators.append("response_too_short")
        if "RESPUESTA FINAL" not in response and len(response) < 100:
            indicators.append("incomplete_processing")
        
        return indicators
    
    def _extract_partial_results(self, response: str) -> Dict[str, Any]:
        """Extract any partial results or useful data from failed attempt"""
        import re
        
        results = {}
        
        # Extract numbers and values
        numbers = re.findall(r'\d+[,.]?\d*', response)
        if numbers:
            results["extracted_numbers"] = numbers[:5]  # First 5 numbers
        
        # Extract dates
        dates = re.findall(r'\d{4}|\d{1,2}/\d{1,2}/\d{2,4}', response)
        if dates:
            results["extracted_dates"] = dates
        
        # Extract currency amounts
        currency = re.findall(r'\$[\d,.]+(?: millones?)?|\d+[,.]?\d* (?:USD|dólares|millones)', response)
        if currency:
            results["extracted_currency"] = currency
        
        # Extract product names (common business terms)
        products = re.findall(r'\b(?:deliproduct|product|producta|producto)\w*\b', response.lower())
        if products:
            results["mentioned_products"] = list(set(products))
        
        # Check if there's structured data (tables, lists)
        if '|' in response or ('\n' in response and any(line.strip().startswith('-') for line in response.split('\n'))):
            results["has_structured_data"] = True
        
        return results
    
    def _assess_data_quality(self, response: str) -> Dict[str, Any]:
        """Assess the quality and completeness of data in the response"""
        quality = {
            "response_length": len(response),
            "has_specific_data": bool(__import__('re').search(r'\d+', response)),
            "completeness_score": min(len(response) / 200, 1.0),  # 0-1 score based on length
            "specificity_score": len(__import__('re').findall(r'\d+[,.]?\d*', response)) / 10,  # Based on number count
            "coherence": "error" not in response.lower() and "no se" not in response.lower()
        }
        
        # Agent-specific quality assessments
        if self.node_name == "sales_analyst":
            quality["has_sales_metrics"] = any(term in response.lower() for term in ['ventas', 'ingresos', 'kilos', 'unidades'])
        elif self.node_name == "text_sql":
            quality["has_query_results"] = '|' in response or 'tabla' in response.lower()
        elif self.node_name == "market_study_agent":
            quality["has_market_insights"] = any(term in response.lower() for term in ['mercado', 'consumidor', 'tendencia', 'segmento'])
        
        return quality
    
    def _assess_completion_level(self, response: str) -> float:
        """Assess how complete the response is (0.0 = not started, 1.0 = complete)"""
        if "RESPUESTA FINAL" in response:
            return 1.0
        elif len(response) > 500:
            return 0.8
        elif len(response) > 200:
            return 0.6
        elif len(response) > 50:
            return 0.4
        elif len(response) > 0:
            return 0.2
        else:
            return 0.0
    
    def _classify_failure_type(self, attempts_data: List[Dict], user_query: str) -> str:
        """Classify the type of failure based on attempts and query"""
        if not attempts_data:
            return "no_attempts"
        
        # Analyze failure indicators across attempts
        all_indicators = []
        for attempt in attempts_data:
            all_indicators.extend(attempt.get("failure_indicators", []))
        
        if "no_data_found" in all_indicators:
            return "data_unavailable"
        elif "error_occurred" in all_indicators:
            return "technical_error"
        elif "agent_limitation" in all_indicators:
            return "agent_capability_limit"
        elif "insufficient_query_detail" in all_indicators:
            return "vague_query"
        elif "timeout_occurred" in all_indicators:
            return "processing_timeout"
        elif "incomplete_processing" in all_indicators:
            return "processing_incomplete"
        else:
            return "unknown_failure"
    
    def _identify_data_issues(self, attempts_data: List[Dict]) -> List[str]:
        """Identify specific data-related issues from the attempts"""
        issues = []
        
        for attempt in attempts_data:
            quality = attempt.get("data_quality", {})
            if not quality.get("has_specific_data", False):
                issues.append("no_specific_data_retrieved")
            if quality.get("completeness_score", 0) < 0.3:
                issues.append("incomplete_data")
            if not quality.get("coherence", True):
                issues.append("incoherent_response")
        
        return list(set(issues))  # Remove duplicates
    
    def _identify_query_problems(self, user_query: str, attempts_data: List[Dict]) -> List[str]:
        """Identify problems with the user query based on failure patterns"""
        problems = []
        
        query_lower = user_query.lower()
        
        # Check if query is too vague
        if len(user_query) < 20:
            problems.append("query_too_short")
        
        if not any(word in query_lower for word in ['cuánto', 'cómo', 'qué', 'cuál', 'dónde', 'cuándo', 'por qué']):
            problems.append("no_clear_question_word")
        
        # Check for missing time context
        if not __import__('re').search(r'\d{4}|mes|año|trimestre|periodo|reciente|actual', query_lower):
            problems.append("no_time_context")
        
        # Agent-specific query problems
        if self.node_name == "sales_analyst" and not any(term in query_lower for term in ['ventas', 'ingresos', 'producto', 'cliente']):
            problems.append("missing_sales_context")
        elif self.node_name == "market_study_agent" and not any(term in query_lower for term in ['mercado', 'consumidor', 'competencia', 'tendencia']):
            problems.append("missing_market_context")
        
        return problems
    
    def _identify_agent_limitations(self, attempts_data: List[Dict]) -> List[str]:
        """Identify specific limitations of this agent based on failed attempts"""
        limitations = []
        
        # Agent-specific limitations
        agent_limits = {
            "sales_analyst": ["requires_specific_time_periods", "needs_product_context", "limited_to_available_sales_data"],
            "market_study_agent": ["limited_to_historical_studies", "requires_specific_market_segments", "depends_on_study_availability"],
            "search_agent": ["depends_on_web_availability", "requires_specific_search_terms", "limited_by_search_relevance"],
            "text_sql": ["requires_valid_database_connection", "limited_to_available_tables", "needs_proper_query_format"]
        }
        
        return agent_limits.get(self.node_name, ["general_processing_limitations"])
    
    def _suggest_alternative_data_sources(self, user_query: str, attempts_data: List[Dict]) -> List[str]:
        """Suggest alternative data sources based on the query and failure pattern"""
        suggestions = []
        
        query_lower = user_query.lower()
        
        if "ventas" in query_lower or "ingresos" in query_lower:
            suggestions.extend(["financial_reports", "sales_database", "business_intelligence_dashboard"])
        
        if "mercado" in query_lower or "competencia" in query_lower:
            suggestions.extend(["market_research_studies", "industry_reports", "competitor_analysis"])
        
        if "cliente" in query_lower or "consumidor" in query_lower:
            suggestions.extend(["customer_surveys", "behavioral_data", "demographic_studies"])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _consolidate_partial_data(self, attempts_data: List[Dict]) -> Dict[str, Any]:
        """Consolidate any useful partial data from all failed attempts"""
        consolidated = {
            "all_numbers_found": [],
            "all_dates_found": [],
            "all_products_mentioned": [],
            "structured_data_available": False,
            "total_content_analyzed": 0
        }
        
        for attempt in attempts_data:
            partial = attempt.get("partial_results", {})
            
            # Consolidate numbers
            if "extracted_numbers" in partial:
                consolidated["all_numbers_found"].extend(partial["extracted_numbers"])
            
            # Consolidate dates
            if "extracted_dates" in partial:
                consolidated["all_dates_found"].extend(partial["extracted_dates"])
            
            # Consolidate products
            if "mentioned_products" in partial:
                consolidated["all_products_mentioned"].extend(partial["mentioned_products"])
            
            # Check for structured data
            if partial.get("has_structured_data", False):
                consolidated["structured_data_available"] = True
            
            consolidated["total_content_analyzed"] += len(attempt.get("content", ""))
        
        # Remove duplicates and limit size
        consolidated["all_numbers_found"] = list(set(consolidated["all_numbers_found"]))[:10]
        consolidated["all_dates_found"] = list(set(consolidated["all_dates_found"]))[:5]
        consolidated["all_products_mentioned"] = list(set(consolidated["all_products_mentioned"]))[:5]
        
        return consolidated


class SimpleNode(BaseNode):
    """
    A simple node implementation for nodes that ALWAYS go to the same route
    regardless of response content (like synthesizer -> supervisor, text_sql -> sales_analyst).
    These nodes don't check for "RESPUESTA FINAL" - they always route the same way.
    """
    
    def __init__(self, agent: Any, node_name: str, target_route: str, max_retries: int = 3):
        super().__init__(agent, node_name, max_retries)
        self.target_route = target_route
    
    def _get_success_route(self) -> str:
        return self.target_route
    
    def _get_continue_route(self) -> str:
        return self.target_route
    
    def _get_fallback_route(self) -> str:
        return self.target_route
        
    def _is_final_response(self, response: str) -> bool:
        """Simple nodes don't check for final response - they always continue to target"""
        return False  # Always "continue" (which goes to target_route)


class ConditionalNode(BaseNode):
    """
    A conditional node implementation for nodes that have different routes
    for success vs. continue (like sales_node -> supervisor vs. text_sql).
    """
    
    def __init__(self, agent: Any, node_name: str, success_route: str, continue_route: str, 
                 fallback_route: str = None, max_retries: int = 3):
        super().__init__(agent, node_name, max_retries)
        self.success_route = success_route
        self.continue_route = continue_route
        self.fallback_route = fallback_route or success_route
    
    def _get_success_route(self) -> str:
        return self.success_route
    
    def _get_continue_route(self) -> str:
        return self.continue_route
    
    def _get_fallback_route(self) -> str:
        return self.fallback_route


class LoopingNode(BaseNode):
    """
    A looping node implementation for nodes that loop back to themselves
    when they don't have a final response (like market_study_node, search_node).
    These check for "RESPUESTA FINAL" and either go to supervisor or loop back to themselves.
    """
    
    def __init__(self, agent: Any, node_name: str, success_route: str = "supervisor", max_retries: int = 3):
        super().__init__(agent, node_name, max_retries)
        self.success_route = success_route
    
    def _get_success_route(self) -> str:
        return self.success_route
    
    def _get_continue_route(self) -> str:
        # Looping nodes go back to themselves when continuing
        return self.node_name
    
    def _get_fallback_route(self) -> str:
        return self.success_route
