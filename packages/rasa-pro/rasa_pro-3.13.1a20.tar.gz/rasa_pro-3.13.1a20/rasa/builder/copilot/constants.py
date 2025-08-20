# A dot-path for importlib to the copilot prompt
from typing import Literal

COPILOT_PROMPTS_DIR = "builder.copilot.prompts"
COPILOT_PROMPTS_FILE = "copilot_system_prompt.jinja2"

# Roles copilot utilizes - Use literal types to avoid type errors with OpenAI
ROLE_USER: Literal["user"] = "user"
ROLE_SYSTEM: Literal["system"] = "system"
ROLE_ASSISTANT: Literal["assistant"] = "assistant"
# Rasa Copilot role - Added to avoid confusion with the assistant role on the frontend.
ROLE_COPILOT: Literal["copilot"] = "copilot"

# Copilot Telemetry
COPILOT_SEGMENT_WRITE_KEY_ENV_VAR = "COPILOT_SEGMENT_WRITE_KEY"
