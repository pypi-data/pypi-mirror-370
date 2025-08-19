import json
import asyncio
import jwt
import os
from fastapi import Request, HTTPException
from botbuilder.core import (
    BotFrameworkAdapter,
    ActivityHandler,
    MessageFactory,
    TurnContext,
    BotFrameworkAdapterSettings,
)
from botbuilder.schema import Activity, ActivityTypes
from botframework.connector.auth import AppCredentials

from utils.logger import logger
from config.params import (
    MicrosoftAppId,
    MicrosoftAppPassword,
    MicrosoftAppTenantId,
)


class BotFramework:
    def __init__(self, engine):
        self.engine = engine
        self.app_id = MicrosoftAppId
        self.adapter = self._create_adapter()
        self.bot = self._create_bot()

    def _create_adapter(self):
        settings = BotFrameworkAdapterSettings(
            app_id=self.app_id,
            app_password=MicrosoftAppPassword,
            channel_auth_tenant=MicrosoftAppTenantId,
        )
        adapter = BotFrameworkAdapter(settings)

        trusted_urls = [
            "https://api.botframework.com",
            "https://botframework.azure.us",
            "https://smba.trafficmanager.net",
            "https://webchat.botframework.com",
            "https://directline.botframework.com",
            "https://productbot.azurewebsites.net",
        ]

        for url in trusted_urls:
            try:
                AppCredentials.trust_service_url(url)
            except Exception as e:
                logger.warning(f"Failed to trust URL {url}: {e}")

        async def on_error(context, error):
            logger.error(f"Bot adapter error: {type(error).__name__}: {error}")
            await context.send_activity(
                MessageFactory.text("I encountered an error. Please try again.")
            )

        adapter.on_turn_error = on_error
        return adapter

    def _create_bot(self):
        class ProductBot(ActivityHandler):
            def __init__(self, engine):
                self.engine = engine

            async def on_message_activity(self, turn_context: TurnContext):
                await turn_context.send_activity(
                    MessageFactory.text("Procesando su consulta. Un momento, por favor.")
                )
                asyncio.create_task(self.process_query_async(turn_context))

            async def process_query_async(self, turn_context: TurnContext):
                try:
                    user_message = turn_context.activity.text
                    user_id = turn_context.activity.from_property.id
                    session_id = turn_context.activity.conversation.id

                    result = self.engine.process_query(
                        user_message, user_name=user_id, session_id=session_id
                    )
                    response_text = self.extract_response(result)
                except Exception as e:
                    logger.error(f"Error processing bot message: {e}")
                    response_text = "Lo siento, ocurrió un error."

                await turn_context.send_activity(MessageFactory.text(response_text))

            def extract_response(self, result):
                if result and result.get("error"):
                    return "Lo siento, he encontrado un problema técnico."
                if result and "messages" in result:
                    synthesizer_messages = [
                        msg
                        for msg in result["messages"]
                        if (hasattr(msg, "name") and msg.name == "synthesizer")
                        or (isinstance(msg, dict) and msg.get("name") == "synthesizer")
                    ]
                    if synthesizer_messages:
                        content = synthesizer_messages[-1].content if hasattr(synthesizer_messages[-1], 'content') else synthesizer_messages[-1].get('content')
                        return content
                    else:
                        content = result["messages"][-1].content if hasattr(result["messages"][-1], 'content') else result["messages"][-1].get('content')
                        return content
                return "Lo siento, no pude procesar tu consulta."

            async def on_members_added_activity(
                self, members_added, turn_context: TurnContext
            ):
                for member in members_added:
                    if member.id != turn_context.activity.recipient.id:
                        await turn_context.send_activity(
                            MessageFactory.text(
                                "¡Hola! Product ProductBot, tu asistente experto. ¿En qué puedo ayudarte?"
                            )
                        )

        return ProductBot(self.engine)

    async def messages_handler(self, request: Request):
        if not self.adapter or not self.bot:
            raise HTTPException(
                status_code=503,
                detail="Bot Framework components not available",
            )

        body = await request.body()
        activity = Activity().deserialize(json.loads(body.decode("utf-8")))
        auth_header = request.headers.get("Authorization", "")

        if os.getenv("ENV") == "local":
            await self.adapter.process_activity(activity, "", self.bot.on_turn)
            return {"status": "ok"}

        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")

        token = auth_header[7:]
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            if decoded.get("aud") != self.app_id:
                raise HTTPException(status_code=401, detail="Invalid audience")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

        await self.adapter.process_activity(activity, auth_header, self.bot.on_turn)
        return {"status": "ok"}

    def options_messages_handler(self):
        return {"status": "ok", "methods": ["POST", "OPTIONS"]}

