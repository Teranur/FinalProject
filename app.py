from botbuilder.core import (
    ConversationState,
    MemoryStorage,
    UserState,
)
from botbuilder.schema import Activity
from botbuilder.integration.aiohttp import BotFrameworkHttpAdapter
from aiohttp import web
from botbuilder.core import BotFrameworkAdapterSettings
from botbuilder.integration.aiohttp import BotFrameworkHttpAdapter
from bot2 import SearchBot
from bot import CovUniChatBot

# Load settings
app_id = "c292f96e-db6f-4937-b0e8-069df21108cc"
app_password = "8496f60a-b17b-46c8-97fe-04603bd8efa6"

# Create adapter
settings = BotFrameworkAdapterSettings(app_id, app_password)
adapter = BotFrameworkHttpAdapter(settings)

# Create memory storage
memory = MemoryStorage()

# Create conversation state
conversation_state = ConversationState(memory)

# Create user state
user_state = UserState(memory)

# Create bot
#BOT = CovUniChatBot()
Bot = SearchBot(conversation_state, user_state)


async def messages(req: web.Request) -> web.Response:
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return web.Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""
    try:
        response = await adapter.process_activity(activity, auth_header, BOT.on_turn)
        if response:
            return web.json_response(data=response.body, status=response.status)
        return web.Response(status=201)
    except Exception as exception:
        raise exception

app = web.Application()
app.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        web.run_app(app, host="localhost", port=3978)
    except Exception as exception:
        raise exception
