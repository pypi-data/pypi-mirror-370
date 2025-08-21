import platform

# Platform Detection Constants
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MACOS = platform.system() == "Darwin"

# Provider Constants
DEFAULT_PROVIDER = "anthropic"  # Can be overridden with MIRRAI_PROVIDER env var

PROVIDER_DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openrouter": "anthropic/claude-sonnet-4",
}

# API Constants
DEFAULT_API_HOST = "0.0.0.0"
DEFAULT_API_PORT = 8777

# Execution Constants
DEFAULT_MAX_ITERATIONS = 50
DEFAULT_MAX_TOKENS = 4096

# Desktop Interaction Constants
WINDOW_FOCUS_DELAY = 0.5
WINDOW_FOCUS_ENSURE_DELAY = 0.1

# Typing speed constants
TYPING_WPM = 777
TYPING_DELAY_MS = int(60000 / (TYPING_WPM * 5))  # Assuming avg word is 5 chars

# Mouse movement parameters
MIN_MOVE_DURATION = 0.2
MAX_MOVE_DURATION = 0.6
PIXELS_PER_SECOND = 1500
SHORT_DISTANCE_THRESHOLD = 200  # pixels

# Specifically related to Anthropic's computer use tool (https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool)
# Doesn't really offer anything besides pre-defined schemas and an optimized system prompt, but it works
ANTHROPIC_COMPUTER_USE_BETA = "computer-use-2025-01-24"
ANTHROPIC_COMPUTER_TOOL_TYPE = "computer_20250124"
