import pyotp, os, json
from crypto import derivar_chave, cifrar_aes_gcm, decifrar_aes_gcm

def cadastrar(username, senha):
    ...

def login(username, senha, codigo_totp):
    ...