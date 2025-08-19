import requests
from langchain_core.tools import StructuredTool
from schemas.vector_search_input import VectorSearchInput
from config.params import (
    DATABRICKS_TOKEN,
    DATABRICKS_HOST,
    MARKET_STUDY_RAG_TABLE,
)
from utils.logger import logger
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, Union, List
import hashlib

# Circuit breaker to prevent repeated identical queries
_query_cache: Dict[str, Tuple[str, datetime]] = {}
_CACHE_DURATION = timedelta(minutes=10)  # Cache results for 10 minutes


def debug_search_years():
    """Debug function to see what years exist in the database"""
    import requests
    from config.params import (
        DATABRICKS_TOKEN,
        DATABRICKS_HOST,
        MARKET_STUDY_RAG_TABLE,
    )

    url = f"https://{DATABRICKS_HOST}/api/2.0/vector-search/indexes/{MARKET_STUDY_RAG_TABLE}/query"
    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "query_text": "year 2008",
        "num_results": 20,  # Get more results
        "columns": ["nombre_archivo", "year"],
        "debug_level": 1,
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    result_text = response.text

    import json

    result_data = json.loads(result_text)

    if "result" in result_data and "data_array" in result_data["result"]:
        data_array = result_data["result"]["data_array"]
        years = set()
        for row in data_array:
            if len(row) > 1:
                years.add(row[1])

        print(f"Years found in unfiltered search for '2008': {sorted(years)}")
        print(f"Total results: {len(data_array)}")

        # Look specifically for any 2008 entries
        found_2008 = False
        for row in data_array:
            if len(row) > 1 and (row[1] == 2008 or row[1] == 2008.0):
                print(f"Found 2008 entry: {row[0]} - year: {row[1]}")
                found_2008 = True

        if not found_2008:
            print("No 2008 entries found in search results")

    return result_text


def vector_search_market_studies(
    query_text: str,
    top_k: int = 5,
    year_filter: Optional[Union[int, List[int]]] = None,
    year_range_start: Optional[int] = None,
    year_range_end: Optional[int] = None,
    category_filter: Optional[str] = None,
    study_type_filter: Optional[str] = None,
) -> str:
    """
    Ejecuta una consulta en el índice vectorial de CompanyName con los filtros proporcionados.

    Args:
        query_text: Texto de consulta.
        top_k: Número de resultados a retornar (1-10, por defecto 5).
               Valores bajos previenen sobrecarga de memoria.
        year_filter: Filtrar por año(s) específico(s). Puede ser un año único o lista de años.
        year_range_start: Año de inicio para filtro de rango (inclusivo).
        year_range_end: Año de fin para filtro de rango (inclusivo).
        category_filter: Filtrar por categoría de producto ('liquido', 'otro', 'powder').
        study_type_filter: Filtrar por tipo de estudio.

    Returns:
        str: Resultados de la búsqueda vectorial como texto plano.
    """
    # Enforce strict limits to prevent memory overload
    top_k = max(1, min(top_k, 10))

    # Create cache key including all parameters for proper caching
    cache_params = f"{query_text}:{top_k}:{year_filter}:{year_range_start}:{year_range_end}:{category_filter}:{study_type_filter}"
    cache_key = hashlib.md5(cache_params.encode()).hexdigest()
    current_time = datetime.now()

    # Check cache first (circuit breaker)
    if cache_key in _query_cache:
        cached_result, cached_time = _query_cache[cache_key]
        if current_time - cached_time < _CACHE_DURATION:
            logger.info(f"Using cached result for query: {query_text[:50]}...")
            return cached_result
        else:
            # Remove expired cache entry
            del _query_cache[cache_key]

    # Clean old cache entries periodically
    if len(_query_cache) > 100:  # Prevent memory bloat
        expired_keys = [
            key
            for key, (_, timestamp) in _query_cache.items()
            if current_time - timestamp > _CACHE_DURATION
        ]
        for key in expired_keys:
            del _query_cache[key]

    # Build the search URL
    url = f"https://{DATABRICKS_HOST}/api/2.0/vector-search/indexes/{MARKET_STUDY_RAG_TABLE}/query"
    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json",
    }

    # Build Databricks filter conditions
    filter_conditions = []
    filter_description_parts = []

    if year_filter:
        if isinstance(year_filter, list):
            condition = f"year IN ({', '.join(map(str, year_filter))})"
            description = f"años: {', '.join(map(str, year_filter))}"
        else:
            condition = f"year = {year_filter}"
            description = f"año: {year_filter}"
        filter_conditions.append(condition)
        filter_description_parts.append(description)

    if year_range_start is not None and year_range_end is not None:
        filter_conditions.append(f"year >= {year_range_start}")
        filter_conditions.append(f"year <= {year_range_end}")
        filter_description_parts.append(f"período: {year_range_start}-{year_range_end}")
    elif year_range_start is not None:
        filter_conditions.append(f"year >= {year_range_start}")
        filter_description_parts.append(f"desde: {year_range_start}")
    elif year_range_end is not None:
        filter_conditions.append(f"year <= {year_range_end}")
        filter_description_parts.append(f"hasta: {year_range_end}")

    if category_filter:
        filter_conditions.append(f"categoria_producto = '{category_filter}'")
        filter_description_parts.append(f"categoría: {category_filter}")

    if study_type_filter:
        filter_conditions.append(f"tipo_estudio = '{study_type_filter}'")
        filter_description_parts.append(f"tipo: {study_type_filter}")

    # Build the base payload
    payload = {
        "query_text": query_text,
        "num_results": top_k,  # Use the actual top_k parameter (max 10)
        "columns": [
            "nombre_archivo",
            "year",
            "categoria_producto",
            "tipo_estudio",
            "resumen",
            "text",
        ],
        "debug_level": 1,
    }

    # Add Databricks filters if any
    if filter_conditions:
        payload["filters"] = {"AND": filter_conditions}
        logger.info(f"Using Databricks filters: {payload['filters']}")

    # Build filter description for logging
    filter_description = ""
    if filter_description_parts:
        filter_description = f" [FILTROS: {', '.join(filter_description_parts)}]"

    logger.info(f"Executing vector search: '{query_text[:50]}...'{filter_description}")

    # Execute the search
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    result_text = response.text

    logger.debug(f"Search payload sent: {payload}")
    logger.debug(f"First 500 chars of search results: {result_text[:500]}")

    # Post-process if necessary
    if filter_conditions:
        logger.info("Applying post-processing for additional filtering")
        try:
            import json

            result_data = json.loads(result_text)

            if "result" in result_data and "data_array" in result_data["result"]:
                data_array = result_data["result"]["data_array"]
                valid_results = []

                for i, row in enumerate(data_array):
                    row_year = row[1]
                    if isinstance(year_filter, list):
                        if row_year in year_filter or int(row_year) in year_filter:
                            valid_results.append(row)
                    else:
                        if row_year == year_filter or int(row_year) == year_filter:
                            valid_results.append(row)

                if valid_results:
                    result_data["result"]["data_array"] = valid_results
                    result_data["result"]["row_count"] = len(valid_results)
                    result_text = json.dumps(result_data)

        except Exception as e:
            logger.warning(f"Could not parse/filter search results: {e}")

    # Cache the result before returning
    _query_cache[cache_key] = (result_text, current_time)

    logger.info(
        f"Vector search completed with {len(result_text)} characters{filter_description}"
    )
    return result_text


vector_search_market_studies_tool = StructuredTool.from_function(
    func=vector_search_market_studies,
    name="vector_search_market_studies",
    description=(
        "Ejecuta una consulta en el índice vectorial de CompanyName con filtros avanzados. "
        "PARÁMETROS: top_k (1-10, default 5) para prevenir sobrecarga de memoria. "
        "FILTROS DISPONIBLES: "
        "- year_filter: Año específico o lista de años [2004, 2008, 2024] "
        "- year_range_start/end: Rango de años (ej. 2020-2024) "
        "- category_filter: 'liquido', 'otro', 'powder' "
        "- study_type_filter: 'estudio cualitativo', 'ad tracking', 'cuas', 'estudio de mercado', 'panel consumidores', 'brand tracking', 'otro' "
        "Usa valores bajos de top_k (3-5) para consultas específicas."
    ),
    args_schema=VectorSearchInput,
)
