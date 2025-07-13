import google.generativeai as genai
import json
import re

class GptConfidence:
    """
    Uses a large language model to evaluate a trading signal and provide a
    confidence score and an expected PnL.
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
            print(f"Failed to configure Gemini API for Confidence check: {e}")
            self.model = None

        self.system_prompt = """
You are a world-class risk manager and quantitative analyst at a proprietary trading firm.
Your task is to evaluate a pre-generated trading signal for XAU/USD based on Smart Money Concepts.
You must analyze the entry price, stop loss, and take profit.
Based on this information, provide your assessment in a strict JSON format ONLY. Do not add any extra text or explanations.

The JSON output must contain these fields:
- "prob": Your estimated probability of the trade hitting Take Profit before Stop Loss. This should be a float between 0.0 and 1.0. A value of 0.7 means a 72% chance of success.
- "expected_pnl": The expected profit or loss in USD for a standard 0.01 lot trade, considering a typical commission of $0.5. Calculate this based on the distance to TP and SL.
- "confidence_label": A string label for your confidence level. Possible values: "High", "Medium", "Low".
- "reasoning": A brief, one-sentence explanation for your assessment.

Example Input Signal:
{ "side": "SELL", "entry_price": 2344.50, "sl": 2350.00, "tp": 2330.00 }

Example JSON Output:
{
  "prob": 0.72,
  "expected_pnl": 14.0,
  "confidence_label": "High",
  "reasoning": "The signal targets a clear liquidity pool with a favorable risk-reward ratio."
}

Now, analyze the following trading signal:
"""

    def get_confidence_for_signal(self, signal: dict) -> dict | None:
        """
        Takes a signal dictionary, sends it to the LLM for evaluation,
        and returns the parsed confidence metrics.
        """
        if not self.model:
            print("--- [GPT CONFIDENCE] Model not initialized. Skipping check. ---")
            # Возвращаем "нейтральный" результат, если GPT недоступен
            return {"prob": 0.5, "expected_pnl": 0, "confidence_label": "Unknown", "reasoning": "GPT not available."}

        # Формируем промпт с данными сигнала
        signal_text = json.dumps(signal)
        full_prompt = self.system_prompt + "\n\n" + signal_text

        try:
            response = self.model.generate_content(full_prompt)
            json_response_str = response.text.strip()
            
            # Очистка ответа от markdown
            if "```json" in json_response_str:
                json_response_str = json_response_str.split("```json")[1].split("```")[0].strip()
            
            parsed_data = json.loads(json_response_str)
            return parsed_data
            
        except Exception as e:
            print(f"--- [GPT CONFIDENCE] Error during confidence check: {e} ---")
            return None