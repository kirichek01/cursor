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
        
        # Получаем контекст для reply сообщений
        context_message = None
        if message_data.get('is_reply'):
            original_msg_id = message_data.get('reply_to_msg_id')
            original_signal = self.db.get_signal_by_message_id(message_data.get('chat_id'), original_msg_id)
            if original_signal:
                context_message = original_signal.get('original_message', '')
                print(f"--- [CONTEXT] Found original message: {context_message[:100]}... ---")
        
        cancellation_keywords = ['cancel', 'отмена', 'close', 'закрыть', 'cancen', 'slose', 'not valid']
        if message_data.get('is_reply') and message_text.strip().lower() in cancellation_keywords:
            print(f"--- [PROCESSOR] Hardcoded cancellation command '{message_text}' detected. Bypassing GPT. ---")
            self.handle_cancellation(message_data)
            return

        # Парсим с контекстом
        parsed_data = self.gpt.parse_signal(message_text, context_message)
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

        # Обработка команд с учетом контекста
        if parsed_data.get('is_hold_command'):
            self.handle_hold_command(message_data)
        elif parsed_data.get('is_cancellation'):
            self.handle_cancellation(message_data, parsed_data)
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
            target_ticket = parsed_data.get('target_ticket')
            partial_close_percent = parsed_data.get('partial_close_percent')
            
            print(f"--- [PROCESSOR] Modifying tickets {tickets} for signal ID {original_signal['id']} ---")
            print(f"--- [PROCESSOR] New SL: {new_sl}, New TP: {new_tp}, Target: {target_ticket}, Partial: {partial_close_percent}% ---")
            
            if partial_close_percent and target_ticket:
                # Частичное закрытие конкретного тикета
                self._partial_close_specific_ticket(tickets, target_ticket, partial_close_percent, original_signal['id'])
            elif target_ticket and len(tickets) > 1:
                # Модификация конкретного тикета
                self._modify_specific_ticket(tickets, target_ticket, new_sl, new_tp, original_signal['id'])
            else:
                # Модификация всех тикетов
                self._modify_all_tickets(tickets, new_sl, new_tp, original_signal['id'])
            
        except Exception as e:
            self.db.add_log("ERROR", f"Error processing modification for signal ID {original_signal['id']}: {e}")

    def _partial_close_specific_ticket(self, tickets, target_ticket, percent, signal_id):
        """Частично закрывает конкретный тикет."""
        ticket_index = self._get_ticket_index(target_ticket)
        
        if ticket_index is not None and ticket_index < len(tickets):
            specific_ticket = tickets[ticket_index]
            success, msg = self.mt5.partial_close_position(specific_ticket, percent)
            
            if success:
                self.db.add_log("SUCCESS", f"Partially closed {percent}% of ticket {specific_ticket} ({target_ticket}).")
            else:
                self.db.add_log("ERROR", f"Failed to partially close ticket {specific_ticket}: {msg}")
        else:
            self.db.add_log("WARNING", f"Could not find specific ticket for {target_ticket}")

    def _modify_specific_ticket(self, tickets, target_ticket, new_sl, new_tp, signal_id):
        """Модифицирует конкретный тикет."""
        ticket_index = self._get_ticket_index(target_ticket)
        
        if ticket_index is not None and ticket_index < len(tickets):
            specific_ticket = tickets[ticket_index]
            success, msg = self.mt5.modify_position_sltp(specific_ticket, new_sl, new_tp)
            
            if success:
                self.db.add_log("SUCCESS", f"Modified specific ticket {specific_ticket} ({target_ticket}) successfully.")
                # Обновляем данные в БД
                self._update_signal_with_modification(signal_id, new_sl, new_tp, tickets, target_ticket)
            else:
                self.db.add_log("ERROR", f"Failed to modify specific ticket {specific_ticket}: {msg}")
        else:
            self.db.add_log("WARNING", f"Could not find specific ticket for {target_ticket}")

    def _modify_all_tickets(self, tickets, new_sl, new_tp, signal_id):
        """Модифицирует все тикеты."""
        for ticket in tickets:
            success, msg = self.mt5.modify_position_sltp(ticket, new_sl, new_tp)
            if success:
                self.db.add_log("SUCCESS", f"Ticket {ticket} modified successfully.")
            else:
                self.db.add_log("ERROR", f"Failed to modify ticket {ticket}: {msg}")
        
        # Обновляем запись в БД новыми данными
        original_signal = self.db.get_signal_by_id(signal_id)
        if original_signal:
            updated_tps = [new_tp] if new_tp is not None else json.loads(original_signal['take_profits'])
            updated_sl = new_sl if new_sl is not None else original_signal['stop_loss']
            self.db.update_signal_with_trade_data(signal_id, updated_sl, updated_tps, tickets, 'MODIFIED_ACTIVE')

    def _get_ticket_index(self, target_ticket):
        """Определяет индекс тикета на основе target_ticket."""
        if target_ticket == "TP1":
            return 0
        elif target_ticket == "TP2":
            return 1
        elif target_ticket == "TP3":
            return 2
        return None

    def _update_signal_with_modification(self, signal_id, new_sl, new_tp, tickets, target_ticket):
        """Обновляет сигнал с учетом модификации конкретного тикета."""
        # Получаем текущие данные сигнала
        original_signal = self.db.get_signal_by_id(signal_id)
        if not original_signal:
            return
        
        # Обновляем только соответствующий TP
        current_tps = json.loads(original_signal['take_profits'])
        ticket_index = self._get_ticket_index(target_ticket)
        
        if ticket_index is not None and ticket_index < len(current_tps):
            if new_tp is not None:
                current_tps[ticket_index] = new_tp
        
        updated_sl = new_sl if new_sl is not None else original_signal['stop_loss']
        self.db.update_signal_with_trade_data(signal_id, updated_sl, current_tps, tickets, 'MODIFIED_ACTIVE')

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

    def handle_hold_command(self, message_data):
        """Обрабатывает команды 'держать' позицию."""
        log_msg = "--- [PROCESSOR] Hold command received. Keeping position open... ---"
        print(log_msg)
        self.db.add_log("INFO", log_msg)

        if not message_data.get('is_reply'):
            self.db.add_log("WARNING", "Hold command received, but it was not a reply.")
            return

        original_signal = self.db.get_signal_by_message_id(message_data.get('chat_id'), message_data.get('reply_to_msg_id'))
        if not original_signal:
            self.db.add_log("WARNING", f"Could not find original signal for hold command.")
            return
        
        # Обновляем статус сигнала на HOLD
        self.db.update_signal_status(original_signal['id'], 'HOLD')
        self.db.add_log("SUCCESS", f"Signal ID {original_signal['id']} set to HOLD status.")

    def handle_cancellation(self, message_data, parsed_data=None):
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
            
            # Проверяем, есть ли целевой тикет для селективной отмены
            target_ticket = parsed_data.get('target_ticket') if parsed_data else None
            
            if target_ticket and len(tickets) > 1:
                # Селективная отмена конкретного тикета
                print(f"--- [PROCESSOR] Selective cancellation for {target_ticket} ---")
                self._cancel_specific_ticket(tickets, target_ticket, original_signal['id'])
            else:
                # Отмена всех тикетов
                print(f"--- [PROCESSOR] Cancelling all tickets {tickets} for signal ID {original_signal['id']} ---")
                self._cancel_all_tickets(tickets, original_signal['id'])
            
        except Exception as e:
            self.db.add_log("ERROR", f"Error processing cancellation for signal ID {original_signal['id']}: {e}")

    def _cancel_specific_ticket(self, tickets, target_ticket, signal_id):
        """Отменяет конкретный тикет на основе контекста."""
        # Определяем индекс тикета на основе target_ticket
        ticket_index = None
        if target_ticket == "TP1":
            ticket_index = 0
        elif target_ticket == "TP2":
            ticket_index = 1
        elif target_ticket == "TP3":
            ticket_index = 2
        
        if ticket_index is not None and ticket_index < len(tickets):
            specific_ticket = tickets[ticket_index]
            success, msg = self.mt5.close_position_by_ticket(specific_ticket)
            if not success:
                success, msg = self.mt5.cancel_pending_order(specific_ticket)
            
            if success:
                self.db.add_log("SUCCESS", f"Specific ticket {specific_ticket} ({target_ticket}) cancelled successfully.")
                # Удаляем тикет из списка и обновляем сигнал
                tickets.pop(ticket_index)
                self.db.update_signal_with_trade_data(signal_id, None, None, tickets, 'PARTIALLY_CANCELLED')
            else:
                self.db.add_log("ERROR", f"Failed to cancel specific ticket {specific_ticket}: {msg}")
        else:
            self.db.add_log("WARNING", f"Could not find specific ticket for {target_ticket}")

    def _cancel_all_tickets(self, tickets, signal_id):
        """Отменяет все тикеты."""
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
        
        self.db.update_signal_status(signal_id, 'CANCELLED') 