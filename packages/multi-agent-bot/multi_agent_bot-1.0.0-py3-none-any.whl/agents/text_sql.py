from config.params import (
    COMPANY_SELL_IN_GENIE_SPACE_ID,
    DATABRICKS_HOST,
    DATABRICKS_TOKEN,
)
from config.prompts import genie_agent_description
from databricks.sdk import WorkspaceClient
from databricks_langchain.genie import GenieAgent

genie_agent = GenieAgent(
    genie_space_id=COMPANY_SELL_IN_GENIE_SPACE_ID,
    genie_agent_name="Genie",
    description=genie_agent_description,
    client=WorkspaceClient(host=DATABRICKS_HOST, token=DATABRICKS_TOKEN),
)
