import os
from databricks_langchain import ChatDatabricks
from langchain_openai import ChatOpenAI

COMPANY_SELL_IN_GENIE_SPACE_ID = os.getenv("COMPANY_SELL_IN_GENIE_SPACE_ID")
SALES_GENIE_SPACE_ID = os.getenv("SALES_GENIE_SPACE_ID")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
MARKET_STUDY_RAG_TABLE = os.getenv("MARKET_STUDY_RAG_TABLE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MICROSOFT_ACCESS_TOKEN = os.getenv("MICROSOFT_ACCESS_TOKEN")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
BRAND_NAME = os.getenv("BRAND_NAME", "Coca-Cola")

if os.getenv("ENV") == "local":
    MicrosoftAppId = ""
    MicrosoftAppPassword = ""
    MicrosoftAppTenantId = ""
else:
    MicrosoftAppId = os.getenv("MicrosoftAppId")
    MicrosoftAppPassword = os.getenv("MicrosoftAppPassword")
    MicrosoftAppTenantId = os.getenv("MicrosoftAppTenantId")

MICROSOFT_APP_ID = MicrosoftAppId
MICROSOFT_APP_PASSWORD = MicrosoftAppPassword
MICROSOFT_APP_TENANT_ID = MicrosoftAppTenantId

# Initialize EXPERTS_LLM based on environment variable
if os.getenv("EXPERTS_LLM", "databricks") == "openai":
    EXPERTS_LLM = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0)
else:
    # Use Databricks LLM by default
    EXPERTS_LLM = ChatDatabricks(
        endpoint="databricks-meta-llama-3-3-70b-instruct",
        temperature=0,
        target_uri="databricks",
    )

# Initialize SUPERVISOR_LLM based on environment variable
if os.getenv("SUPERVISOR_LLM", "openai") == "databricks":
    SUPERVISOR_LLM = ChatDatabricks(
        endpoint="databricks-meta-llama-3-3-70b-instruct",
        temperature=0,
        target_uri="databricks",
    )
else:
    # Use OpenAI by default for supervisor
    SUPERVISOR_LLM = ChatOpenAI(
        model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0
    )
