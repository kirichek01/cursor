import json
from datetime import datetime

class SignalProcessor:
    def __init__(self, db_service, gpt_service, mt5_service, settings, channels, page):
        self.db = db_service
        self.gpt = gpt_service
        self.mt5 = mt5_service
        self.settings = settings
        self.channels = channels
        self.page = page

    def update_settings(self, new_settings):
        print("--- [PROCESSOR] Settings updated. ---")
        self.settings = new_settings

    def update_channels(self, new_channels_dict):
        self.channels = new_channels_dict

    def _get_contextual_symbol(self, channel_id):
        channel_config = self.channels.get(str(channel_id))
        if not channel_config:
            return None
        weekday = datetime.today().weekday()
        if weekday >= 5:
            symbol = channel_config.get('weekend_symbol')
            if symbol:
                print(f"--- [CONTEXT] It's the weekend. Using weekend symbol: {symbol} ---")
                return symbol
        return channel_config.get('default_symbol')

    def process_new_message(self, message_data):
        channel_id = str(message_data.get('chat_id'))
        if channel_id not in self.channels or not self.channels[channel_id].get('active', False):
            return
        
        message_text = message_data.get('text')
        if not message_text:
            return

        print(f"\n--- [PROCESSOR] New message from '{message_data.get('channel_name')}' ---")
        
        cancellation_keywords = ['cancel', 'отмена', 'close', 'закрыть', 'cancen', 'slose', 'not valid']
        if message_data.get('is_reply') and message_text.strip().lower() in cancellation_keywords:
            print(f"--- [PROCESSOR] Hardcoded cancellation command '{message_text}' detected. Bypassing GPT. ---")
            self.handle_cancellation(message_data)
            return

        parsed_data = self.gpt.parse_signal(message_text)
        print(f"--- [GPT] Parsed Data: {parsed_data} ---")
        if not parsed_data:
            self.db.add_log('ERROR', "GPT parsing failed.")
            return
        
        parsed_data['channel_id'] = message_data.get('chat_id')
        parsed_data['message_id'] = message_data.get('message_id')
        parsed_data['channel_name'] = message_data.get('channel_name')
        parsed_data['original_message'] = message_text

        # --- Symbol alias mapping (supports dict or list) ---
        symbol_map_raw = self.settings.get('symbol_mapping', {})
        if isinstance(symbol_map_raw, list):
            _map = {}
            for item in symbol_map_raw:
                if isinstance(item, dict):
                    for k, v in item.items():
                        _map[k.upper()] = v
            symbol_map = _map
        elif isinstance(symbol_map_raw, dict):
            symbol_map = {k.upper(): v for k, v in symbol_map_raw.items()}
        else:
            symbol_map = {}

        raw_symbol = (parsed_data.get('symbol') or '').upper()
        if raw_symbol and raw_symbol in symbol_map:
            parsed_data['symbol'] = symbol_map[raw_symbol]
        elif not parsed_data.get('symbol'):
            parsed_data['symbol'] = self._get_contextual_symbol(channel_id)
        # --- End alias mapping ---
        
        if parsed_data.get('symbol'):
            symbol_mapping = self.settings.get('symbol_mapping', {})
            raw_symbol = parsed_data['symbol'].upper()
            if raw_symbol in symbol_mapping:
                parsed_data['symbol'] = symbol_mapping[raw_symbol]
        else:
            parsed_data['symbol'] = self._get_contextual_symbol(channel_id)
        
        if not parsed_data.get('symbol'):
             self.db.add_log('INFO', f"Message from {parsed_data['channel_name']} did not contain a symbol.")
             return

        if parsed_data.get('is_cancellation'):
            self.handle_cancellation(message_data)
        elif parsed_data.get('is_modification'):
            self.handle_modification(parsed_data, message_data)
        elif parsed_data.get('entry_price') and not parsed_data.get('stop_loss'):
            self.handle_partial_entry(parsed_data)
        elif parsed_data.get('stop_loss') and not parsed_data.get('entry_price'):
            self.handle_sl_tp_update(parsed_data, message_data)
        elif parsed_data.get('order_type') and (parsed_data.get('stop_loss') or parsed_data.get('take_profits')):
            self.handle_full_signal(parsed_data)
        else:
            self.db.add_log('INFO', f"Message from {parsed_data['channel_name']} did not contain a recognizable trade action.")

    def handle_full_signal(self, parsed_data):
        print("--- [PROCESSOR] Handling as a full signal. ---")
        signal_id = self.db.add_signal(parsed_data, status='NEW')
        if signal_id:
            self._execute_trade(signal_id, parsed_data)

    def handle_partial_entry(self, parsed_data):
        print(f"--- [PROCESSOR] Handling as a partial entry for {parsed_data.get('symbol')}. ---")
        self.db.add_signal(parsed_data, status='PARTIAL_ENTRY')
        self.db.add_log('INFO', f"Partial signal with entry point saved. Waiting for SL/TP.")

    def handle_sl_tp_update(self, parsed_data, message_data):
        print(f"--- [PROCESSOR] Handling as an SL/TP update for {parsed_data.get('symbol')}. ---")
        partial_signal = None
        if message_data.get('is_reply'):
            original_msg_id = message_data.get('reply_to_msg_id')
            partial_signal = self.db.get_signal_by_message_id(message_data.get('chat_id'), original_msg_id)
        if not partial_signal:
            partial_signal = self.db.get_latest_partial_signal(parsed_data['channel_id'], parsed_data['symbol'])
        if not partial_signal:
            self.db.add_log('WARNING', f"Received SL/TP update, but no partial signal was found for {parsed_data.get('symbol')}.")
            return
        
        full_signal_data = dict(partial_signal)
        full_signal_data['stop_loss'] = parsed_data['stop_loss']
        full_signal_data['take_profits'] = parsed_data['take_profits']
        self._execute_trade(full_signal_data['id'], full_signal_data)
        
    def handle_modification(self, parsed_data, message_data):
        print("--- [PROCESSOR] Modification command received. ---")
        if not message_data.get('is_reply'):
            self.db.add_log("WARNING", "Modification ignored: it was not a reply.")
            return
        
        original_msg_id = message_data.get('reply_to_msg_id')
        original_signal = self.db.get_signal_by_message_id(message_data.get('chat_id'), original_msg_id)
        if not original_signal:
            self.db.add_log("WARNING", f"Could not find original signal for replied message ID {original_msg_id} to modify.")
            return
        
        tickets_json = original_signal['mt5_tickets']
        if not tickets_json:
            self.db.add_log("WARNING", f"Original signal ID {original_signal['id']} has no MT5 tickets to modify.")
            return
        
        try:
            tickets = json.loads(tickets_json)
            new_sl = parsed_data.get('stop_loss')
            new_tp = parsed_data.get('take_profits')[0] if parsed_data.get('take_profits') else None
            
            print(f"--- [PROCESSOR] Modifying tickets {tickets} for signal ID {original_signal['id']} with SL: {new_sl}, TP: {new_tp} ---")
            for ticket in tickets:
                success, msg = self.mt5.modify_position_sltp(ticket, new_sl, new_tp)
                if success:
                    self.db.add_log("SUCCESS", f"Ticket {ticket} modified successfully.")
                else:
                    self.db.add_log("ERROR", f"Failed to modify ticket {ticket}: {msg}")
            
            # Обновляем запись в БД новыми данными
            updated_tps = [new_tp] if new_tp is not None else json.loads(original_signal['take_profits'])
            updated_sl = new_sl if new_sl is not None else original_signal['stop_loss']
            self.db.update_signal_with_trade_data(original_signal['id'], updated_sl, updated_tps, tickets, 'MODIFIED_ACTIVE')

        except Exception as e:
            self.db.add_log("ERROR", f"Error processing modification for signal ID {original_signal['id']}: {e}")

    def _execute_trade(self, signal_id, trade_data):
        if not trade_data.get('take_profits') and not trade_data.get('stop_loss'):
             self.db.update_signal_status(signal_id, 'ERROR_NO_TP_SL')
             return
        volume_per_tp = self.settings.get('trading', {}).get('lot_per_tp', 0.01)
        if volume_per_tp < 0.01:
            self.db.update_signal_status(signal_id, 'ERROR_INVALID_VOLUME')
            return

        print(f"--- [PROCESSOR] Calling MT5 to place trade for signal ID {signal_id} ---")
        success, message = self.mt5.place_order(trade_data, volume_per_tp)
        
        if success:
            try:
                tickets_str = message.split('[')[1].split(']')[0]
                tickets = [int(t.strip()) for t in tickets_str.split(',') if t.strip()]
                self.db.update_signal_with_trade_data(signal_id, trade_data.get('stop_loss'), trade_data.get('take_profits', []), tickets, 'PROCESSED_ACTIVE')
            except Exception as e:
                self.db.update_signal_status(signal_id, 'ERROR_TICKET_PARSE')
        else:
            error_log = f"--- [PROCESSOR] Failed to place trade for signal ID {signal_id}. Reason: {message} ---"
            print(error_log)
            self.db.add_log('ERROR', error_log)
            self.db.update_signal_status(signal_id, 'ERROR_MT5')

    def handle_cancellation(self, message_data):
        log_msg = "--- [PROCESSOR] Cancellation command received. Trying to find original signal... ---"
        print(log_msg)
        self.db.add_log("INFO", log_msg)

        if not message_data.get('is_reply'):
            self.db.add_log("WARNING", "Cancellation received, but it was not a reply.")
            return

        original_signal = self.db.get_signal_by_message_id(message_data.get('chat_id'), message_data.get('reply_to_msg_id'))
        if not original_signal:
            self.db.add_log("WARNING", f"Could not find original signal for replied message ID {message_data.get('reply_to_msg_id')}.")
            return
        
        tickets_json = original_signal['mt5_tickets']
        if not tickets_json:
            self.db.add_log("WARNING", f"Original signal ID {original_signal['id']} has no MT5 tickets to cancel.")
            return
        
        try:
            tickets = json.loads(tickets_json)
            print(f"--- [PROCESSOR] Cancelling tickets {tickets} for signal ID {original_signal['id']} ---")
            
            for ticket in tickets:
                # Try to close position first
                success, msg = self.mt5.close_position_by_ticket(ticket)
                if not success:
                    # If closing fails, try to cancel pending order
                    success, msg = self.mt5.cancel_pending_order(ticket)
                
                if success:
                    self.db.add_log("SUCCESS", f"Ticket {ticket} cancelled successfully.")
                else:
                    self.db.add_log("ERROR", f"Failed to cancel ticket {ticket}: {msg}")
            
            self.db.update_signal_status(original_signal['id'], 'CANCELLED')
            
        except Exception as e:
            self.db.add_log("ERROR", f"Error processing cancellation for signal ID {original_signal['id']}: {e}") 