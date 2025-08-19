from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from api.super_engine import engine
from api.sales_engine import sales_engine
from api.market_study_engine import market_study_engine
from api.search_engine import search_engine
from utils.logger import logger
from schemas.api_query_request import QueryRequest
from api.bot_framework import BotFramework


# Import the Bot engine - must happen AFTER MLflow configuration

app = FastAPI(
    title="Multi-Agent Bot API",
    description="API para interactuar con el sistema de agentes especializados en investigación de mercado.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Bot Framework
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Include OPTIONS for Bot Framework
    allow_headers=["*"],  # Allow all headers for now
)


@app.get("/")
async def read_root():
    return {"status": "ok", "message": "Multi-Agent Bot API is running"}


@app.get("/api/version")
async def get_version():
    """Get API version and deployment info"""
    import datetime
    return {
        "version": "1.0.1",
        "deployment_time": "2025-08-07T19:48:00Z",
        "git_commit": "latest",
        "status": "deployed_with_requirements_fix"
    }


@app.post("/api/query")
async def process_query(request: QueryRequest):
    """
    Process a user query through the Multi-Agent engine

    Returns the result of the multi-agent analysis.
    """
    try:
        logger.info(f"Received query: {request.query} from user_id: {request.user_id}")

        # Use the user_id as the user_name if provided, otherwise use "user"
        user_name = request.user_id if request.user_id else "user"

        # Process the query through the Multi-Agent engine with user name and session
        result = engine.process_query(
            request.query, user_name=user_name, session_id=request.session_id
        )

        logger.info(f"Engine result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """
    Check if the Multi-Agent Bot API is healthy and the engine is properly initialized
    """
    try:
        # Check if the engine is properly initialized
        if engine.bot_runner:
            return {"status": "healthy", "engine": "initialized"}
        else:
            return {"status": "degraded", "engine": "not initialized"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


# Initialize Bot Framework with the super engine
bot_framework = BotFramework(engine)


@app.post("/api/messages")
async def messages(request: Request):
    return await bot_framework.messages_handler(request)


@app.options("/api/messages")
async def options_messages():
    return bot_framework.options_messages_handler()


# ===== SALES ENGINE ENDPOINTS =====


@app.post("/api/sales/query")
async def process_sales_query(request: QueryRequest):
    """
    Process a sales-specific query through the SalesBot engine

    This endpoint is optimized for sales analysis and provides focused
    sales insights without the broader research team coordination.
    """
    try:
        logger.info(
            f"Received sales query: {request.query} from user_id: {request.user_id}"
        )

        # Use the user_id as the user_name if provided, otherwise use "user"
        user_name = request.user_id if request.user_id else "user"

        # Process the query through the Sales Engine with session management
        result = sales_engine.process_query(
            request.query, user_name=user_name, session_id=request.session_id
        )

        logger.info(f"Sales engine result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing sales query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sales/summary")
async def get_sales_summary(user_id: str = "api_user"):
    """
    Get a comprehensive sales summary and overview

    Returns general sales trends, key metrics, and insights.
    """
    try:
        logger.info(f"Generating sales summary for user_id: {user_id}")

        result = sales_engine.get_sales_summary(user_name=user_id)

        logger.info(f"Sales summary generated successfully")
        return result
    except Exception as e:
        logger.error(f"Error generating sales summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sales/product/{product_name}")
async def analyze_product_performance(product_name: str, user_id: str = "api_user"):
    """
    Analyze the sales performance of a specific product

    Args:
        product_name: Name of the product to analyze (e.g., "product name")
        user_id: User identifier for tracking

    Returns detailed performance analysis including trends and comparisons.
    """
    try:
        logger.info(
            f"Analyzing product performance for '{product_name}' - user_id: {user_id}"
        )

        result = sales_engine.analyze_product_performance(
            product_name, user_name=user_id
        )

        logger.info(f"Product analysis completed for '{product_name}'")
        return result
    except Exception as e:
        logger.error(f"Error analyzing product '{product_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sales/regional")
async def get_regional_analysis(region: str = None, user_id: str = "api_user"):
    """
    Get regional sales analysis

    Args:
        region: Specific region to analyze (optional)
        user_id: User identifier for tracking

    If no region is specified, returns analysis comparing all regions.
    """
    try:
        if region:
            logger.info(
                f"Generating regional analysis for '{region}' - user_id: {user_id}"
            )
        else:
            logger.info(
                f"Generating comparative regional analysis - user_id: {user_id}"
            )

        result = sales_engine.get_regional_analysis(region=region, user_name=user_id)

        logger.info(f"Regional analysis completed")
        return result
    except Exception as e:
        logger.error(f"Error generating regional analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sales/time-series")
async def get_time_series_analysis(
    period: str = "últimos 12 meses", user_id: str = "api_user"
):
    """
    Get time series sales analysis

    Args:
        period: Time period to analyze (e.g., "2023", "últimos 6 meses", "2022-2023")
        user_id: User identifier for tracking

    Returns analysis of sales patterns and trends over time.
    """
    try:
        logger.info(
            f"Generating time series analysis for period '{period}' - user_id: {user_id}"
        )

        result = sales_engine.get_time_series_analysis(period=period, user_name=user_id)

        logger.info(f"Time series analysis completed for period '{period}'")
        return result
    except Exception as e:
        logger.error(f"Error generating time series analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sales/health")
async def sales_health_check():
    """
    Check the health status of the Sales Engine

    Returns status information about the sales engine and its components.
    """
    try:
        result = sales_engine.health_check()
        return result
    except Exception as e:
        logger.error(f"Sales engine health check failed: {e}")
        return {"status": "unhealthy", "engine": "sales_engine", "error": str(e)}


# ===== MARKET STUDY ENGINE ENDPOINTS =====


@app.post("/api/market-study/query")
async def process_market_study_query(request: QueryRequest):
    """
    Process a market study-specific query through the MarketStudyBot engine

    This endpoint is optimized for qualitative market research analysis
    and provides insights based on market studies conducted between 2004-2024.
    """
    try:
        logger.info(
            f"Received market study query: {request.query} from user_id: {request.user_id}"
        )

        # Use the user_id as the user_name if provided, otherwise use "user"
        user_name = request.user_id if request.user_id else "user"

        # Process the query through the Market Study Engine with session management
        result = market_study_engine.process_query(
            request.query, user_name=user_name, session_id=request.session_id
        )

        logger.info(f"Market study engine result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing market study query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market-study/trends")
async def get_market_trends(period: str = "2020-2024", user_id: str = "api_user"):
    """
    Get market trends analysis for a specific period

    Args:
        period: Time period to analyze (e.g., "2020-2024", "últimos 5 años")
        user_id: User identifier for tracking

    Returns analysis of market trends and consumer preference changes.
    """
    try:
        logger.info(
            f"Generating market trends analysis for period '{period}' - user_id: {user_id}"
        )

        result = market_study_engine.get_market_trends(period=period, user_name=user_id)

        logger.info(f"Market trends analysis completed for period '{period}'")
        return result
    except Exception as e:
        logger.error(f"Error generating market trends analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market-study/consumer-behavior")
async def analyze_consumer_behavior(segment: str = None, user_id: str = "api_user"):
    """
    Analyze consumer behavior patterns

    Args:
        segment: Specific consumer segment to analyze (optional)
        user_id: User identifier for tracking

    If no segment is specified, returns general consumer behavior analysis.
    """
    try:
        if segment:
            logger.info(
                f"Analyzing consumer behavior for segment '{segment}' - user_id: {user_id}"
            )
        else:
            logger.info(
                f"Analyzing general consumer behavior patterns - user_id: {user_id}"
            )

        result = market_study_engine.analyze_consumer_behavior(
            segment=segment, user_name=user_id
        )

        logger.info(f"Consumer behavior analysis completed")
        return result
    except Exception as e:
        logger.error(f"Error analyzing consumer behavior: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market-study/competitive-analysis")
async def get_competitive_analysis(competitor: str = None, user_id: str = "api_user"):
    """
    Get competitive market analysis

    Args:
        competitor: Specific competitor to analyze (optional)
        user_id: User identifier for tracking

    If no competitor is specified, returns general competitive landscape analysis.
    """
    try:
        if competitor:
            logger.info(
                f"Generating competitive analysis for '{competitor}' - user_id: {user_id}"
            )
        else:
            logger.info(f"Generating general competitive analysis - user_id: {user_id}")

        result = market_study_engine.get_competitive_analysis(
            competitor=competitor, user_name=user_id
        )

        logger.info(f"Competitive analysis completed")
        return result
    except Exception as e:
        logger.error(f"Error generating competitive analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market-study/brand-perception/{brand_name}")
async def analyze_brand_perception(brand_name: str, user_id: str = "api_user"):
    """
    Analyze brand perception and positioning

    Args:
        brand_name: Brand name to analyze (e.g., "CompanyName")
        user_id: User identifier for tracking

    Returns detailed brand perception analysis including attributes and positioning.
    """
    try:
        logger.info(
            f"Analyzing brand perception for '{brand_name}' - user_id: {user_id}"
        )

        result = market_study_engine.get_brand_perception(
            brand=brand_name, user_name=user_id
        )

        logger.info(f"Brand perception analysis completed for '{brand_name}'")
        return result
    except Exception as e:
        logger.error(f"Error analyzing brand perception for '{brand_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market-study/segmentation")
async def get_market_segmentation(user_id: str = "api_user"):
    """
    Get market segmentation analysis

    Args:
        user_id: User identifier for tracking

    Returns analysis of market segments, consumer characteristics and preferences.
    """
    try:
        logger.info(f"Generating market segmentation analysis - user_id: {user_id}")

        result = market_study_engine.get_market_segmentation(user_name=user_id)

        logger.info(f"Market segmentation analysis completed")
        return result
    except Exception as e:
        logger.error(f"Error generating market segmentation analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market-study/health")
async def market_study_health_check():
    """
    Check the health status of the Market Study Engine

    Returns status information about the market study engine and its components.
    """
    try:
        result = market_study_engine.health_check()
        return result
    except Exception as e:
        logger.error(f"Market study engine health check failed: {e}")
        return {"status": "unhealthy", "engine": "market_study_engine", "error": str(e)}


# ===== SEARCH ENGINE ENDPOINTS =====


@app.post("/api/search/query")
async def process_search_query(request: QueryRequest):
    """
    Process a general-purpose search query through the SearchEngine
    """
    try:
        logger.info(
            f"Received search query: {request.query} from user_id: {request.user_id}"
        )

        # Use the user_id as the user_name if provided, otherwise use "user"
        user_name = request.user_id if request.user_id else "user"

        # Process the query through the Search Engine with session management
        result = search_engine.process_query(
            request.query, user_name=user_name, session_id=request.session_id
        )

        logger.info(f"Search engine result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing search query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search/market-trends")
async def get_market_trends(
    topic: str = "generic products",
    region: str = "Central America",
    user_id: str = "api_user",
):
    """
    Get market trends analysis for a specific topic and region
    """
    try:
        logger.info(
            f"Searching market trends for topic '{topic}' in '{region}' - user_id: {user_id}"
        )

        result = search_engine.search_market_trends(
            topic=topic, region=region, user_name=user_id
        )

        logger.info(f"Market trends search completed for topic '{topic}'")
        return result
    except Exception as e:
        logger.error(f"Error searching market trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search/competitors")
async def research_competitors(
    company: str = "CompanyName",
    industry: str = "productos genericos",
    user_id: str = "api_user",
):
    """
    Research competitors and competitive landscape
    """
    try:
        logger.info(
            f"Researching competitors for company '{company}' in '{industry}' - user_id: {user_id}"
        )

        result = search_engine.research_competitors(
            company=company, industry=industry, user_name=user_id
        )

        logger.info(f"Competitor research completed for company '{company}'")
        return result
    except Exception as e:
        logger.error(f"Error researching competitors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search/industry-news")
async def analyze_industry_news(
    industry: str = "food and beverage",
    keywords: str = "generic products",
    user_id: str = "api_user",
):
    """
    Analyze recent industry news and developments
    """
    try:
        logger.info(
            f"Analyzing industry news for '{industry}' with keywords '{keywords}' - user_id: {user_id}"
        )

        result = search_engine.analyze_industry_news(
            industry=industry, keywords=keywords, user_name=user_id
        )

        return result
    except Exception as e:
        logger.error(f"Error analyzing industry news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search/health")
async def search_health_check():
    """
    Check the health status of the Search Engine

    Returns status information about the search engine and its components.
    """
    try:
        result = search_engine.health_check()
        return result
    except Exception as e:
        logger.error(f"Search engine health check failed: {e}")
        return {"status": "unhealthy", "engine": "search_engine", "error": str(e)}
