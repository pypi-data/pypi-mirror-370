import os


MODEL_TOKEN_CONFIGS = dict({
    "gpt-3.5-turbo": dict(
        safe_buffer=16,
        hard_roof=4096,
        min_answer_room=512,
    ),
    # gpt4 config here
})

OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY", "not set")
