import asyncio
import threading
from telethon import TelegramClient, events

class TelegramService:
    """
    Handles all interactions with the Telegram API via Telethon.
    This service runs in a separate thread to listen for new messages without
    blocking the main GUI thread. It uses Flet's page.pubsub to communicate back to the UI.
    """
    def __init__(self, session_name, api_id, api_hash, page):
        self.session_name = session_name
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = None
        self.loop = None
        self.page = page
        self.is_running = False
        self.thread = None

    def start(self):
        """
        Starts the Telegram client in a new thread with asyncio event loop.
        """
        if self.is_running:
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._run_client, daemon=True)
        self.thread.start()

    def _run_client(self):
        """
        Runs the Telegram client in a separate thread.
        """
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash, loop=self.loop)
            
            # Register the event handler for new messages
            self.client.on(events.NewMessage)(self._message_handler)

            # Emit status update
            self.page.pubsub.send_all_on_topic("telegram_status", "CONNECTING")
            
            self.client.start()
            
            # Emit status update
            self.page.pubsub.send_all_on_topic("telegram_status", "CONNECTED")
            
            # Keep the event loop running
            self.client.run_until_disconnected()

        except Exception as e:
            error_message = f"Telegram Error: {e}"
            print(error_message)
            self.page.pubsub.send_all_on_topic("telegram_status", f"ERROR: {e}")
        finally:
            self.page.pubsub.send_all_on_topic("telegram_status", "DISCONNECTED")
            self.is_running = False
            if self.loop:
                self.loop.close()

    async def _message_handler(self, event):
        """
        Event handler for when a new message is received.
        It extracts relevant information and sends it via pubsub to the main thread.
        """
        chat = await event.get_chat()
        sender = await event.get_sender()
        
        # Prepare data to be sent to the main thread
        message_data = {
            'chat_id': event.chat_id,
            'channel_name': getattr(chat, 'title', 'N/A'),
            'message_id': event.message.id,
            'text': event.message.text,
            'date': event.message.date,
            'is_reply': event.message.is_reply,
            'reply_to_msg_id': event.message.reply_to_msg_id if event.message.is_reply else None
        }
        
        # Send the message data via pubsub
        self.page.pubsub.send_all_on_topic("new_telegram_message", message_data)

    def stop(self):
        """Stops the Telegram client gracefully."""
        self.is_running = False
        if self.client and self.client.is_connected():
            # Use run_coroutine_threadsafe to call async code from a non-async thread
            asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)

    def fetch_dialogs(self):
        """
        Asynchronously fetches the user's dialogs (chats, channels).
        This method is designed to be called from the main thread.
        """
        if not self.client or not self.loop:
            return
        # Schedule the coroutine to run on the service's event loop
        future = asyncio.run_coroutine_threadsafe(self._get_dialogs_async(), self.loop)

    async def _get_dialogs_async(self):
        """The actual async implementation to get dialogs."""
        dialogs_list = []
        try:
            async for dialog in self.client.iter_dialogs():
                if dialog.is_channel:
                    dialogs_list.append({'id': dialog.id, 'name': dialog.name})
            self.page.pubsub.send_all_on_topic("dialogs_fetched", dialogs_list)
        except Exception as e:
            print(f"Error fetching dialogs: {e}")
            self.page.pubsub.send_all_on_topic("dialogs_fetched", []) # Send empty list on error 