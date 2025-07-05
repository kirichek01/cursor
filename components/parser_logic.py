import asyncio
from telethon import TelegramClient, events

class ParserLogic:
    """
    Handles all interactions with the Telegram API via Telethon.
    This version is adapted for Flet and uses page.pubsub for communication.
    """
    def __init__(self, session_name, api_id, api_hash, page):
        self.session_name = session_name
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = None
        self.loop = None
        self.page = page # Flet page object for pubsub

    def start(self):
        """
        Starts the Telegram client in a new asyncio event loop.
        This method should be run in a separate thread.
        """
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash, loop=self.loop)
            self.client.on(events.NewMessage)(self._message_handler)

            self.page.pubsub.send_all({"type": "status", "data": "CONNECTING"})
            self.client.start()
            self.page.pubsub.send_all({"type": "status", "data": "CONNECTED"})
            
            self.client.run_until_disconnected()

        except Exception as e:
            self.page.pubsub.send_all({"type": "status", "data": f"ERROR: {e}"})
        finally:
            self.page.pubsub.send_all({"type": "status", "data": "DISCONNECTED"})
            if self.loop:
                self.loop.close()

    async def _message_handler(self, event):
        """
        Event handler for a new message. Emits data via page.pubsub.
        """
        chat = await event.get_chat()
        
        message_data = {
            'type': 'new_message',
            'data': {
                'channel_name': getattr(chat, 'title', 'N/A'),
                'text': event.message.text,
                'date': event.message.date.strftime("%Y-%m-%d %H:%M:%S"),
            }
        }
        self.page.pubsub.send_all(message_data)

    def stop(self):
        """Stops the Telegram client gracefully."""
        if self.client and self.client.is_connected() and self.loop:
            asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)

    def fetch_dialogs(self):
        if not self.client or not self.loop:
            return
        future = asyncio.run_coroutine_threadsafe(self._get_dialogs_async(), self.loop)

    async def _get_dialogs_async(self):
        dialogs_list = []
        try:
            async for dialog in self.client.iter_dialogs():
                if dialog.is_channel:
                    dialogs_list.append({'id': dialog.id, 'name': dialog.name})
            self.page.pubsub.send_all({"type": "dialogs", "data": dialogs_list})
        except Exception as e:
            print(f"Error fetching dialogs: {e}")
            self.page.pubsub.send_all({"type": "dialogs", "data": []}) 