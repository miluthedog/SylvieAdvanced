from os import environ
from dotenv import load_dotenv, dotenv_values

load_dotenv()
env_vars = dotenv_values(".env")
secret = {**env_vars, **environ}


class ID:
    main_channel = 1242439205406244954
    voice_channel = 1249733414601625610
    rules_channel = 1135394985777315971

    default_role = 1284370701318357003
    admin_role = 1116342281432211467


class token:
    discord = secret.get("DISCORDTOKEN")
