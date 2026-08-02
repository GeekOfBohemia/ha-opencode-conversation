"""Constants for OpenCode Conversation."""

from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME

DOMAIN = "opencode_conversation"

CONF_MODEL = "model"
CONF_SERVER = "server"
CONF_SYSTEM_PROMPT = "system_prompt"
CONF_AGENT = "agent"

DEFAULT_USERNAME = "opencode"
DEFAULT_MODEL = "opencode/big-pickle"
DEFAULT_AGENT = "build"
DEFAULT_SYSTEM_PROMPT = (
    "Jsi konverzační agent pro chytrou domácnost postavenou na Home Assistantu. "
    "Odpovídej stručně a věcně, v jazyce uživatele."
)

# Ports and paths are part of the opencode serve HTTP API (https://opencode.ai/docs/server/).
API_HEALTH = "/global/health"
API_SESSION = "/session"
API_MESSAGE = "/session/{session_id}/message"

TIMEOUT_SECONDS = 180
