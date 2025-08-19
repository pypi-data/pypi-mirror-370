from config.params import TAVILY_API_KEY
from utils.tavily import DynamicTavilySearch


# Custom TavilySearch class that adds logging while preserving runtime parameter capability


# Enhanced web search tool with runtime parameter configuration and logging
# The LLM can dynamically adjust these parameters during invocation:
# - include_domains: Restrict to specific domains (e.g., ['wikipedia.org'])
# - exclude_domains: Exclude specific domains
# - search_depth: 'basic' for quick results, 'advanced' for comprehensive search
# - include_images: True to include relevant images
# - time_range: 'day', 'week', 'month', 'year' for recent content
# - topic: 'general', 'news', 'finance' for specialized search
web_search_tool = DynamicTavilySearch(
    tavily_api_key=TAVILY_API_KEY,
    max_results=5,
    topic="general",  # Can be overridden at runtime
    include_answer=True,  # Include AI-generated answers (fixed at init)
    include_raw_content=False,  # Keep responses concise (fixed at init)
    include_images=False,  # Can be overridden at runtime
    include_image_descriptions=False,
    search_depth="advanced",  # Can be overridden at runtime
    time_range=None,  # Can be set at runtime
    include_domains=None,  # Can be set at runtime
    exclude_domains=None,  # Can be set at runtime
)
