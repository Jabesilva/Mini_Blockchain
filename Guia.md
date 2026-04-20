├── main.py           # menu de texto
├── auth.py           # cadastro, login, TOTP
├── crypto.py         # AES-GCM, PBKDF2, derivação de chave
├── blockchain.py     # estrutura de blocos, encadeamento, validação
├── storage.py        # leitura/escrita de arquivos
└── data/
    ├── users.json     # usuários (salt em claro, hash da senha, TOTP key cifrada)
    └── chain.json     # blocos da blockchain

-----------------------------

[crypto.py] não depende de ninguém — é a base
[auth.py] chama crypto.py para derivar chaves e cifrar o TOTP
[blockchain.py] chama crypto.py para cifrar/decifrar dados dos blocos
[storage.py] lê e escreve JSON

=== crypto.py ===

derivar_chave =  senha (str) + salt (bytes) → PBKDF2 (600k iterações) → chave de 32 bytes
                 ⚠ mesmo senha + mesmo salt = mesma chave sempre
                 ⚠ salt diferente = chave completamente diferente

cifrar =  chave + dados (str) → gera IV aleatório (12 bytes) → AES-GCM → retorna (IV, ciphertext)
          ⚠ IV nunca se repete — gerado com os.urandom(12) a cada chamada

decifrar =  chave + IV + ciphertext → AES-GCM → dados originais (str)
            se alguém alterou o ciphertext → lança InvalidTag automaticamente 

=== blockchain.py ===

hash_bloco =  bloco (dict) → serializa campos públicos (owner, ts, iv, cipher, hash_prev)
              → json.dumps(sort_keys=True) → SHA-256 → string hex de 64 chars

criar_bloco =  dados + owner + chave_sessao + chain atual
               → hash_prev = hash_bloco(chain[-1])  ← ou "000...0" se for o primeiro
               → (iv, ciphertext) = cifrar(chave_sessao, dados)
               → retorna dict {owner, timestamp, hash_prev, iv, ciphertext}

validar_chain =  para cada bloco i :
                 recalcula hash_bloco(i-1) e compara com chain[i]["hash_prev"]
                 se diferente → retorna (False, i)  ← índice do bloco corrompido
                 se todos OK  → retorna (True, -1)

=== storage.py ===

carregar_usuarios =  lê data/users.json → retorna dict  (retorna {} se arquivo não existe)

salvar_usuarios =  recebe dict completo de usuários → sobrescreve data/users.json inteiro

carregar_chain =  lê data/chain.json → retorna list  (retorna [] se arquivo não existe)

salvar_chain =  recebe list completa de blocos → sobrescreve data/chain.json inteiro

=== main.py ===

fluxo geral =  usuário escolhe opção no menu
               → se opção exige login e chave_sessao is None → bloqueia
               → senão → executa e atualiza estado em memória

opção cadastro =  pede username + senha → auth.cadastrar() → salvar_usuarios()

opção login =  pede username + senha + TOTP
               → chave_sessao, usuario_atual = auth.login()
               → se None → "credenciais inválidas"

opção add bloco =  [requer login] pede dados → blockchain.criar_bloco()
                   → chain.append(novo_bloco) → salvar_chain()

opção leitura =  [requer login] chain = carregar_chain() → blockchain.validar_chain()
                 para cada bloco:
                     se bloco["owner"] == usuario_atual → tenta decifrar → exibe
                     senão → exibe "[bloco de outro usuário — cifrado]"
                     se InvalidTag → exibe "[ALERTA: bloco adulterado!]"

=== auth.py ===

cadastrar =  pede username + senha
             → verifica se username já existe em users.json → se sim, erro
             → salt = os.urandom(16)
             → chave = derivar_chave(senha, salt)
             → totp_secret = pyotp.random_base32()
             → (iv, totp_cifrado) = cifrar(chave, totp_secret)
             → salva {salt.hex(), iv.hex(), totp_cifrado.hex()} em users.json
             → exibe totp_secret UMA vez na tela para o usuário configurar no app
             ⚠ totp_secret nunca é salvo em claro — só a versão cifrada


login =  pede username + senha + código TOTP
         → carrega {salt, iv, totp_cifrado} do users.json
         → se username não existe → erro genérico (não revelar qual campo errou)
         → chave = derivar_chave(senha, bytes.fromhex(salt))
         → tenta decifrar totp_secret = decifrar(chave, iv, totp_cifrado)
             se InvalidTag → senha errada → erro genérico
         → valida pyotp.TOTP(totp_secret).verify(codigo_totp)
             se False → TOTP inválido → erro genérico
         → chave_sessao = os.urandom(32)
         → retorna (chave_sessao, username)
         ⚠ chave_sessao não vai para arquivo — só retorna para o main.py guardar em RAM
         ⚠ erro genérico em todos os casos = "usuário ou senha inválidos"
            (nunca dizer qual campo específico falhou — evita enumeração de usuários)