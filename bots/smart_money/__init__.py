"""
Smart Money Bot Module

SmartMoney торговый бот с AI анализом:
- SMCBot: основной класс бота
- SMCBotCore: ядро бота с торговой логикой  
- SMCRunner: менеджер запуска и управления
- AIAgent: AI агент для принятия решений
"""

# Импортируем только core функции для серверного окружения
try:
    from .smc_bot_core import load_mt5_data, generate_smc_features, run_strategy
    SMC_CORE_AVAILABLE = True
except ImportError:
    SMC_CORE_AVAILABLE = False

try:
    from .smc_runner import SMCRunner
    SMC_RUNNER_AVAILABLE = True
except ImportError:
    SMC_RUNNER_AVAILABLE = False

try:
    from .ai_agent import AIAgent
    AI_AGENT_AVAILABLE = True
except ImportError:
    AI_AGENT_AVAILABLE = False

try:
    from .config import SMC_CONFIG
    CONFIG_AVAILABLE = True
except ImportError:
    SMC_CONFIG = {}
    CONFIG_AVAILABLE = False

# GUI компоненты доступны только в графическом окружении
try:
    from .smc_bot import SMCBot
    SMC_BOT_AVAILABLE = True
except ImportError:
    SMC_BOT_AVAILABLE = False

__all__ = [
    'SMCBot',
    'load_mt5_data',
    'generate_smc_features', 
    'run_strategy',
    'SMCRunner',
    'AIAgent',
    'SMC_CONFIG'
]