import google.generativeai as genai
import json
import re

class GptService:
    """
    Handles all interactions with the Google Gemini API.
    This version can parse trade modification commands.
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
You are an expert financial analyst. Your task is to parse trading messages into a structured JSON format. Return ONLY the JSON.

**Analysis Rules:**

1.  **Action Identification (Highest Priority):**
    * **Cancellation:** Does the message cancel a trade? Keywords: "cancel", "close", "отмена", "закрыть", "not valid". If yes, set `is_cancellation: true` and all other fields to null/empty.
    * **Modification:** Does the message modify an existing trade? Keywords: "move sl", "new tp", "передвинуть стоп", "новый тейк". If yes, set `is_modification: true` and parse ONLY the new SL/TP values.
    * **New Signal:** If it's not a cancellation or modification, treat it as a new signal.

2.  **Field Extraction:**
    * `symbol`: The instrument (e.g., BTCUSD, GOLD).
    * `order_type`: `BUY`, `SELL`, `BUY_LIMIT`, `SELL_LIMIT`.
    * `entry_price`: The entry price.
    * `stop_loss`, `take_profits`: List of SL/TP values.
    * `is_cancellation`: `true` or `false`.
    * `is_modification`: `true` or `false`.

**Examples:**

* **New Full Signal:** "Buy BTCUSD now, SL 67000, TP 69500" -> `{"symbol": "BTCUSD", "order_type": "BUY", "entry_price": null, "stop_loss": 67000.0, "take_profits": [69500.0], "is_cancellation": false, "is_modification": false}`
* **New Partial (Entry):** "Buy zone GOLD 3374/72" -> `{"symbol": "GOLD", "order_type": "BUY_LIMIT", "entry_price": 3373.0, "stop_loss": null, "take_profits": [], "is_cancellation": false, "is_modification": false}`
* **Modification (Reply):** "Move SL to 3370" -> `{"symbol": null, "order_type": null, "entry_price": null, "stop_loss": 3370.0, "take_profits": [], "is_cancellation": false, "is_modification": true}`
* **Cancellation (Reply):** "Cancel" -> `{"symbol": null, "order_type": null, "entry_price": null, "stop_loss": null, "take_profits": [], "is_cancellation": true, "is_modification": false}`

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

    def parse_signal(self, message_text):
        if not message_text or not self.model:
            return None
        
        full_prompt = self.system_prompt + "\n\nHere is the message to parse:\n" + message_text
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
            # Ensure default values for modification/cancellation flags
            if 'is_modification' not in parsed_data:
                parsed_data['is_modification'] = False
            if 'is_cancellation' not in parsed_data:
                parsed_data['is_cancellation'] = False
                
            return parsed_data
        except Exception as e:
            print(f"An unexpected error occurred in Gemini parse_signal: {e}")
            return None 