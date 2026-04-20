import hashlib, json, time
from crypto import *

def hash_bloco(bloco: dict) -> str:
    # hash sobre campos públicos do bloco
    conteudo = json.dumps({
        "owner": bloco["owner"],
        "timestamp": bloco["timestamp"],
        "hash_prev": bloco["hash_prev"],
        "iv": bloco["iv"],
        "ciphertext": bloco["ciphertext"]
    }, sort_keys=True)
    return hashlib.sha256(conteudo.encode()).hexdigest()

def criar_bloco(dados, owner, chave_sessao, chain):
    hash_prev = hash_bloco(chain[-1]) if chain else "0" * 64
    iv, ciphertext = cifrar_aes_gcm(chave_sessao, dados)
    bloco = {
        "owner": owner,
        "timestamp": time.time(),
        "hash_prev": hash_prev,
        "iv": iv.hex(),
        "ciphertext": ciphertext.hex()
    }
    return bloco

def validar_chain(chain):
    for i in range(1, len(chain)):
        if chain[i]["hash_prev"] != hash_bloco(chain[i-1]):
            return False, i   # cadeia quebrada no bloco i
    return True, -1
    