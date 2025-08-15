from os import environ
from dotenv import load_dotenv, dotenv_values

load_dotenv()
env_vars = dotenv_values(".env")
secret = {**env_vars, **environ}


class ID:
    pha = 754703228003942522
    pha_con = 754703510360162425


class token:
    discord = secret.get("DISCORDTOKEN")
    gemini = secret.get("GEMINIAPIKEY")


class prompt:
    system_prompt = """
    You are a smart assistant with access to tools on multiple servers.

    You have a limit of **Turn**(either text, function call or both) per task. Plan carefully.

    Your job:
    1. Understand the user's request fully before acting by analysing it step-by-step.
    2. Use tools in **parallel** when tasks are independent.
    3. Use **sequential** calls only when one result depends on another.
    4. Avoid unnecessary steps — combine or batch operations when possible.
    5. Think before executing. Finish the task **accurately** and **within the limit**.

    Bad examples:
    - Breaking simple tasks into too many steps
    - Using 3 turns for 1 + 2 + 3
    - Good: 1 + 2 → + 3 → Final answer (2 turns)
    - Best: If supported, do all at once (1 turn)

    Always minimize turns. Finish the task correctly.
    """