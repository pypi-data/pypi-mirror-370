from langchain_tavily import TavilySearch
from typing import Any, Dict
from utils.logger import logger
import json


class DynamicTavilySearch(TavilySearch):
    """TavilySearch with comprehensive logging similar to vector_search.

    This preserves the original TavilySearch functionality where runtime parameters
    can be passed to invoke() and override the instantiation parameters.
    """

    def invoke(self, input: Dict[str, Any], config=None, **kwargs) -> str:
        """Invoke the search with logging.

        According to the documentation, these parameters can be passed at runtime:
        - query (required)
        - include_domains, exclude_domains, search_depth, include_images, time_range

        Parameters set during invocation override those set during instantiation.
        """

        # Debug logging to see what input we're getting
        logger.debug(f"Tavily tool input received: {input}")
        logger.debug(
            f"Input type: {type(input)}, keys: {list(input.keys()) if isinstance(input, dict) else 'Not a dict'}"
        )

        # Extract parameters from input - handle both direct format and tool call format
        if "args" in input and isinstance(input["args"], dict):
            # LangChain tool call format: {'name': '...', 'args': {'query': '...'}, 'id': '...', 'type': 'tool_call'}
            args = input["args"]
            query = args.get("query", "")
            runtime_params = {
                k: v for k, v in args.items() if k != "query" and v is not None
            }
            logger.debug(f"Using tool call format - args: {args}")
        else:
            # Direct format: {'query': '...', 'search_depth': '...'}
            query = input.get("query", "")
            runtime_params = {
                k: v for k, v in input.items() if k != "query" and v is not None
            }
            logger.debug(f"Using direct format")

        logger.debug(f"Extracted query: '{query}' (length: {len(query)})")
        logger.debug(f"Runtime params: {runtime_params}")

        # Build parameter description for logging
        params_used = []
        if runtime_params.get("include_domains"):
            params_used.append(
                f"domains: {', '.join(runtime_params['include_domains'])}"
            )
        if runtime_params.get("exclude_domains"):
            params_used.append(
                f"exclude: {', '.join(runtime_params['exclude_domains'])}"
            )
        if runtime_params.get("search_depth"):
            params_used.append(f"depth: {runtime_params['search_depth']}")
        if runtime_params.get("include_images"):
            params_used.append("images: enabled")
        if runtime_params.get("time_range"):
            params_used.append(f"time: {runtime_params['time_range']}")
        if runtime_params.get("topic"):
            params_used.append(f"topic: {runtime_params['topic']}")
        if runtime_params.get("include_favicon"):
            params_used.append("favicon: enabled")
        if runtime_params.get("start_date") or runtime_params.get("end_date"):
            start = runtime_params.get("start_date", "start")
            end = runtime_params.get("end_date", "end")
            params_used.append(f"dates: {start} to {end}")

        params_description = ""
        if params_used:
            params_description = f" [PARAMS: {', '.join(params_used)}]"

        # Log the search execution
        logger.info(f"Executing Tavily search: '{query[:50]}...'{params_description}")

        try:
            # Execute the parent's invoke method - this handles runtime parameter override
            result = super().invoke(input, config, **kwargs)

            # Debug: Log the raw result before any processing
            logger.debug(f"Raw Tavily result type: {type(result)}")
            logger.debug(f"Raw Tavily result (first 1000 chars): {str(result)[:1000]}")

            # Parse and log result summary
            try:
                # Handle ToolMessage format returned by LangChain
                if hasattr(result, "content"):
                    # It's a ToolMessage, extract the content
                    content = result.content
                    if isinstance(content, str):
                        result_data = json.loads(content)
                    else:
                        result_data = (
                            content if isinstance(content, dict) else {"results": []}
                        )
                elif isinstance(result, str):
                    result_data = json.loads(result)
                else:
                    result_data = (
                        result if isinstance(result, dict) else {"results": []}
                    )

                # Extract summary information for logging
                num_results = len(result_data.get("results", []))
                has_answer = bool(result_data.get("answer"))
                has_images = len(result_data.get("images", [])) > 0

                # Enhanced result logging - show actual results found
                result_details = []
                result_urls = []
                for i, res in enumerate(
                    result_data.get("results", [])[:5]
                ):  # First 5 results
                    title = res.get("title", "No title")[:80]  # Longer titles
                    url = res.get("url", "No URL")[:100]  # Show URLs
                    score = res.get("score", "No score")
                    result_details.append(f"{i + 1}. {title}")
                    result_urls.append(f"   URL: {url} (score: {score})")

                summary_parts = [f"{num_results} results"]
                if has_answer:
                    summary_parts.append("with AI answer")
                if has_images:
                    summary_parts.append(f"{len(result_data.get('images', []))} images")

                logger.info(
                    f"Tavily search completed: {', '.join(summary_parts)}{params_description}"
                )

                if result_details:
                    logger.info("Search results found:")
                    for detail, url in zip(
                        result_details[:3], result_urls[:3]
                    ):  # Top 3 for INFO level
                        logger.info(f"  {detail}")
                        logger.debug(f"  {url}")  # URLs at DEBUG level
                else:
                    logger.warning(
                        f"No search results found for query: '{query[:50]}...'"
                    )

                # Log AI answer if present
                if has_answer:
                    answer_preview = str(result_data.get("answer", ""))[:200]
                    logger.info(f"AI Answer preview: {answer_preview}...")

                # Log full result structure for debugging
                result_str = (
                    json.dumps(result_data)
                    if isinstance(result_data, dict)
                    else str(result)
                )
                logger.debug(f"Full search response structure: {result_str[:1000]}")

                return result

            except (json.JSONDecodeError, TypeError, AttributeError) as e:
                logger.warning(
                    f"Could not parse Tavily search results for logging: {e}"
                )
                result_str = str(result)
                logger.info(f"Tavily search completed (raw result){params_description}")
                logger.debug(f"First 500 chars of search results: {result_str[:500]}")
                return result

        except Exception as e:
            logger.error(f"Tavily search failed: {e}{params_description}")
            raise
