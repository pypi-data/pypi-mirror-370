from databricks_langchain import ChatDatabricks


class ChatDB:
    def __init__(self, endpoint: str = "") -> ChatDatabricks:
        self.endpoint = endpoint
        self.chat = ChatDatabricks(endpoint=self.endpoint, temperature=0)

    def invoke(self):
        return self.chat
