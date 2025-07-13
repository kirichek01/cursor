import google.generativeai as genai
import json
import re

class GptService:
    """
    Handles all interactions with the Google Gemini API.
    This version can parse trade modification commands with context awareness.
    """
    def __init__(self, api_key):
        if not api_key:
            self.model = None
            self.api_key = None
            return
        self.api_key = api_key
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            print(f"Failed to configure Gemini API: {e}")
            self.model = None

        self.system_prompt = """
You are an expert financial analyst specializing in parsing GOLDHUNTER trading signals. Your task is to parse trading messages into a structured JSON format. Return ONLY the JSON.

**GOLDHUNTER Signal Analysis Rules:**

1. **Context Awareness (Highest Priority):**
   - **Reply Messages:** If message is a reply, analyze the context of the original message
   - **Specific Ticket Targeting:** "Cancel TP1" means cancel only the first take profit, not all orders
   - **Partial Modifications:** "Move SL to 2340" modifies only the specific order being replied to
   - **Hold Commands:** "Держать", "Hold", "Keep" means don't close, continue monitoring

2. **Action Identification:**
   - **Cancellation:** "cancel", "close", "отмена", "закрыть", "not valid"
   - **Modification:** "move sl", "new tp", "передвинуть стоп", "новый тейк"
   - **Hold Command:** "держать", "hold", "keep", "продолжаем"
   - **New Signal:** Full entry with SL/TP

3. **Multiple Orders Support:**
   - **TP1, TP2, TP3:** Each take profit is a separate order with unique ticket
   - **Partial Close:** "Close 50% at TP1" closes only specific portion
   - **Selective Cancellation:** "Cancel TP2" cancels only second take profit
   - **Trailing Stop:** "Move SL to breakeven" moves stop loss to entry price

4. **Field Extraction:**
   - `symbol`: The instrument (XAUUSD, EURUSD, GBPUSD, etc.)
   - `order_type`: `BUY`, `SELL`, `BUY_LIMIT`, `SELL_LIMIT`
   - `entry_price`: The entry price from "at PRICE"
   - `stop_loss`: The stop loss from "SL: PRICE"
   - `take_profits`: Array of TP values [TP1, TP2, TP3]
   - `is_cancellation`: `true` for cancellation commands
   - `is_modification`: `true` for modification commands
   - `is_hold_command`: `true` for hold/keep commands
   - `target_ticket`: Specific ticket to modify (from context)
   - `partial_close_percent`: Percentage to close (e.g., 50)

**Examples:**

* **New Signal:** "BUY XAUUSD at 2345.50, SL: 2340.00, TP1: 2350.00, TP2: 2355.00"
* **Modification (Reply):** "Move SL to 2342.00" -> `{"is_modification": true, "stop_loss": 2342.00}`
* **Selective Cancellation:** "Cancel TP2" -> `{"is_cancellation": true, "target_ticket": "TP2"}`
* **Hold Command:** "Держать позицию" -> `{"is_hold_command": true}`
* **Partial Close:** "Close 50% at TP1" -> `{"is_modification": true, "partial_close_percent": 50, "target_ticket": "TP1"}`

Now, analyze the following message:
"""

    @staticmethod
    def test_api_key(api_key_to_test):
        if not api_key_to_test:
            return False
        try:
            genai.configure(api_key=api_key_to_test)
            for _ in genai.list_models():
                pass
            return True
        except Exception:
            return False

    def parse_signal(self, message_text, context_message=None):
        if not message_text or not self.model:
            return None
        
        # Добавляем контекст, если это reply сообщение
        context_info = ""
        if context_message:
            context_info = f"\n\n**Context (Original Message):**\n{context_message}\n\n**Reply Message:**\n{message_text}"
        else:
            context_info = f"\n\nHere is the message to parse:\n{message_text}"
        
        full_prompt = self.system_prompt + context_info
        try:
            response = self.model.generate_content(full_prompt)
            json_response_str = response.text.strip()
            
            if "```json" in json_response_str:
                json_response_str = json_response_str.split("```json")[1].split("```")[0].strip()
            elif json_response_str.startswith("{") and json_response_str.endswith("}"):
                 pass
            else:
                match = re.search(r'\{.*\}', json_response_str, re.DOTALL)
                if match:
                    json_response_str = match.group(0)
                else:
                    raise json.JSONDecodeError("No valid JSON object found in the response.", json_response_str, 0)

            parsed_data = json.loads(json_response_str)
            
            # Ensure default values for all flags
            if 'is_modification' not in parsed_data:
                parsed_data['is_modification'] = False
            if 'is_cancellation' not in parsed_data:
                parsed_data['is_cancellation'] = False
            if 'is_hold_command' not in parsed_data:
                parsed_data['is_hold_command'] = False
            if 'target_ticket' not in parsed_data:
                parsed_data['target_ticket'] = None
            if 'partial_close_percent' not in parsed_data:
                parsed_data['partial_close_percent'] = None
                
            return parsed_data
        except Exception as e:
            print(f"An unexpected error occurred in Gemini parse_signal: {e}")
            return None 