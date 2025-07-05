import json, pathlib
CONFIG_FILE = pathlib.Path.home() / ".combine_trade_bot.json"
DEFAULT = {
    "telegram": {"api_id": "", "api_hash": "", "session_file": "", "channels": []},
    "openai_api_key": "",
    "signal_txt_path": str(pathlib.Path.home()/ "signal.txt"),
    "theme": "dark"
}
def load():
    if CONFIG_FILE.exists():
        try:
            DEFAULT.update(json.loads(CONFIG_FILE.read_text(encoding='utf-8')))
        except Exception:
            pass
    return DEFAULT
def save(cfg: dict):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding='utf-8')
