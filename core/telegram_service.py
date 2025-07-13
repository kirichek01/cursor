import asyncio
from telethon import TelegramClient, events
from PySide6.QtCore import QObject, Signal

class TelegramService(QObject):
    """
    Handles all interactions with the Telegram API via Telethon.
    This service runs in a separate thread to listen for new messages without
    blocking the main GUI thread. It uses Qt Signals to communicate back to the UI.
    This replaces and improves upon the logic in [cite: uploaded:CombineTradeBot/core/telegram_client.py].
    """
    # Define Qt signals to communicate with the main thread
    # Signal to emit when a new message is received
    new_message_signal = Signal(dict)
    # Signal to emit status updates (e.g., 'CONNECTING', 'CONNECTED', 'DISCONNECTED')
    status_signal = Signal(str)
    # Signal to emit the list of dialogs
    dialogs_fetched_signal = Signal(list)

    def __init__(self, session_name, api_id, api_hash, parent=None):
        super().__init__(parent)
        self.session_name = session_name
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = None
        self.loop = None

    def start(self):
        """
        Starts the Telegram client in a new asyncio event loop.
        This method should be run in a separate QThread.
        """
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash, loop=self.loop)
            
            # Register the event handler for new messages
            self.client.on(events.NewMessage)(self._message_handler)

            self.status_signal.emit('CONNECTING')
            self.client.start()
            self.status_signal.emit('CONNECTED')
            
            # Keep the event loop running
            self.client.run_until_disconnected()

        except Exception as e:
            error_message = f"Telegram Error: {e}"
            print(error_message)
            self.status_signal.emit(f"ERROR: {e}")
        finally:
            self.status_signal.emit('DISCONNECTED')
            if self.loop:
                self.loop.close()

    async def _message_handler(self, event):
        """
        Event handler for when a new message is received.
        It extracts relevant information and emits a signal to the main thread.
        This fulfills the requirement to parse messages and replies. [cite: uploaded:CombineTradeBot/README.md]
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
        
        # Emit the signal with the message data dictionary
        self.new_message_signal.emit(message_data)

    def stop(self):
        """Stops the Telegram client gracefully."""
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
        # We don't wait for the result here; the result is emitted via a signal.

    async def _get_dialogs_async(self):
        """The actual async implementation to get dialogs."""
        dialogs_list = []
        try:
            async for dialog in self.client.iter_dialogs():
                if dialog.is_channel:
                    dialogs_list.append({'id': dialog.id, 'name': dialog.name})
            self.dialogs_fetched_signal.emit(dialogs_list)
        except Exception as e:
            print(f"Error fetching dialogs: {e}")
            self.dialogs_fetched_signal.emit([]) # Emit empty list on error

