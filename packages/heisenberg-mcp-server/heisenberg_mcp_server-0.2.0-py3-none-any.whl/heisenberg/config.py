from decouple import config

HEISENBERG_KEY = config("HEISENBERG_KEY")
HEISENBERG_INFERENCE_SERVICE_URL = config(
    "HEISENBERG_INFERENCE_SERVICE_URL", default="https://narrative.agent.heisenberg.so"
)
HEISENBERG_TOKEN = config("HEISENBERG_TOKEN")
HEISENBERG_AGENTS_URL = config(
    "HEISENBERG_AGENTS_URL", default="https://cook-api.heisenberg.so"
)
