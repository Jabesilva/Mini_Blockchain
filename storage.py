import json, os

USERS_FILE = "data/users.json"
CHAIN_FILE = "data/chain.json"

def carregar_usuarios() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def salvar_usuarios(usuarios: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(usuarios, f, indent=2)

def carregar_chain() -> list:
    if not os.path.exists(CHAIN_FILE):
        return []
    with open(CHAIN_FILE, "r") as f:
        return json.load(f)

def salvar_chain(chain: list):
    with open(CHAIN_FILE, "w") as f:
        json.dump(chain, f, indent=2)