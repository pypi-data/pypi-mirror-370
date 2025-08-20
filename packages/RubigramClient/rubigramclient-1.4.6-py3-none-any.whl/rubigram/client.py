from __future__ import annotations
from typing import Optional, Callable, Awaitable
from aiohttp import web
from functools import wraps
from rubigram.types import Update, InlineMessage
from rubigram.method import Method
from rubigram.filters import Filter
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

class Client(Method):
    def __init__(self, token: str, endpoint: Optional[str] = None, host: str = "0.0.0.0", port: int = 8000):
        self.token = token
        self.endpoint = endpoint
        self.host = host
        self.port = port
        self.offset_id = None
        self.routes = web.RouteTableDef()
        self.message_handlers = []
        self.inline_handlers = []
        super().__init__(token)

    def on_message(self, *filters: Filter):
        def decorator(func: Callable[[Client, Update], Awaitable]):
            @wraps(func)
            async def wrapper(client: Client, update: Update):
                try:
                    combined_filter = filters[0] if filters else None
                    for filter in filters[1:]:
                        combined_filter = combined_filter & filter
                    
                    if combined_filter is None or await combined_filter(update):
                        await func(client, update)
                        return True
                    return False
                except Exception as e:
                    logger.exception(f"Error in message handler {func.__name__}: {e}")
                    return False
            self.message_handlers.append(wrapper)
            return func
        return decorator


    def on_inline_message(self, *filters: Filter):
        def decorator(func: Callable[[Client, InlineMessage], Awaitable]):
            @wraps(func)
            async def wrapper(client: Client, update: InlineMessage):
                try:
                    combined_filter = filters[0] if filters else None
                    for filter in filters[1:]:
                        combined_filter = combined_filter & filter
                    
                    if combined_filter is None or await combined_filter(update):
                        await func(client, update)
                        return True
                    return False
                except Exception as e:
                    logger.exception(f"Error in inline handler {func.__name__}: {e}")
                    return False
            self.inline_handlers.append(wrapper)
            return func
        return decorator


    async def dispatch_update(self, update: Update):
        for handler in self.message_handlers:
            try:
                matched = await handler(self, update)
                if matched:
                    return
            except Exception as error:
                logger.exception(f"Error in handler dispatch: {error}")

    async def dispatch_inline(self, update: InlineMessage):
        for handler in self.inline_handlers:
            try:
                matched = await handler(self, update)
                if matched:
                    return
            except Exception as error:
                logger.exception(f"Error in inline handler dispatch: {error}")

    async def updater(self, data: dict):
        if "inline_message" in data:
            event = InlineMessage.from_dict(data["inline_message"])
            await self.dispatch_inline(event)
        elif "update" in data:
            event = Update.from_dict(data["update"])
            event.client = self
            await self.dispatch_update(event)
            
    async def set_endpoints(self):
        if self.endpoint:
            await self.update_bot_endpoint(f"{self.endpoint}/ReceiveUpdate", "ReceiveUpdate")
            await self.update_bot_endpoint(f"{self.endpoint}/ReceiveInlineMessage", "ReceiveInlineMessage")

    def run(self):
        if self.endpoint:
            @self.routes.post("/ReceiveUpdate")
            async def receive_update(request: web.Request):
                data = await request.json()
                await self.updater(data)
                return web.json_response({"status": "OK"})

            @self.routes.post("/ReceiveInlineMessage")
            async def receive_inline_message(request: web.Request):
                data = await request.json()
                await self.updater(data)
                return web.json_response({"status": "OK"})

            app = web.Application()
            app.add_routes(self.routes)
            
            async def on_startup(_):
                await self.set_endpoints()
            app.on_startup.append(on_startup)
            web.run_app(app, host=self.host, port=self.port)
            
        else:
            async def polling():
                while True:
                    try:
                        get_update = await self.get_update(100, self.offset_id)
                        if get_update.updates:
                            updates = get_update.updates
                            for update in updates:
                                if update.type == "NewMessage":
                                    message_time = int(update.new_message.time)
                                elif update.type == "UpdatedMessage":
                                    message_time = int(update.updated_message.time)
                                else:
                                    continue

                                now = int(datetime.now().timestamp())
                                if message_time >= now or message_time + 2 >= now:
                                    if isinstance(update, Update):
                                        update.client = self
                                    await self.dispatch_update(update)

                            self.offset_id = get_update.next_offset_id
                    except Exception as e:
                        logger.exception(f"Polling error: {e}")
                        await asyncio.sleep(1)

            try:asyncio.run(polling())
            except:pass