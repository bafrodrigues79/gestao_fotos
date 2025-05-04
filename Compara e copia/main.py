import os
import shutil
import json
import logging
import sys  # Para forçar a saída do programa

# Criar handlers separadamente
file_handler = logging.FileHandler("processo.log", encoding="utf-8")
stream_handler = logging.StreamHandler()

# Criar o formatador
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Configurar o logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def carregar_configuracao(ficheiro_config):
    """Carrega as diretorias do ficheiro config.json. Termina a execução em caso de erro."""
    logging.info(f"📥 Tentando carregar configuração de '{ficheiro_config}'...")
    try:
        with open(ficheiro_config, 'r') as f:
            config = json.load(f)
            logging.info(f"✅ Configuração carregada com sucesso: {config}")
            return config
    except FileNotFoundError:
        logging.error(f"❌ Ficheiro '{ficheiro_config}' não encontrado. A execução será interrompida.")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f"❌ Erro ao interpretar '{ficheiro_config}'. Verifique o formato JSON. A execução será interrompida.")
        sys.exit(1)

def obter_lista_ficheiros_recursivo(diretorio):
    """Obtém a lista completa de ficheiros, excluindo '$RECYCLE.BIN'. Termina a execução em caso de erro."""
    if not os.path.exists(diretorio):
        logging.error(f"❌ Diretoria '{diretorio}' não encontrada. A execução será interrompida.")
        sys.exit(1)

    logging.info(f"🔍 Analisando diretoria: {diretorio}...")
    ficheiros = set()
    for root, _, files in os.walk(diretorio):
        if "$RECYCLE.BIN" in root:
            logging.warning(f"⚠️ Ignorado: {root} (pasta protegida)")
            continue
        for file in files:
            ficheiro_relativo = os.path.relpath(os.path.join(root, file), diretorio)
            ficheiros.add(ficheiro_relativo)

    logging.info(f"📂 Diretoria '{diretorio}' analisada. {len(ficheiros)} ficheiros encontrados.")
    return ficheiros

def gerar_nome_sem_colisao(destino, nome_ficheiro):
    """Gera um novo nome para ficheiros que já existem no destino."""
    base, ext = os.path.splitext(nome_ficheiro)
    contador = 1
    novo_nome = nome_ficheiro

    while os.path.exists(os.path.join(destino, novo_nome)):
        novo_nome = f"{base}({contador}){ext}"
        contador += 1

    logging.warning(f"⚠️ Ficheiro existente renomeado: {nome_ficheiro} → {novo_nome}")
    return novo_nome

def copiar_diferencas(origem, destino):
    """Compara ficheiros e copia apenas os que não existem no destino, renomeando se necessário. Termina a execução em caso de erro."""
    logging.info(f"📥 Iniciando processo de cópia de '{origem}' para '{destino}'.")

    if not os.path.exists(origem):
        logging.error(f"❌ Diretoria de origem '{origem}' não encontrada. A execução será interrompida.")
        sys.exit(1)

    if not os.path.exists(destino):
        os.makedirs(destino)
        logging.info(f"📁 Diretoria de destino '{destino}' criada.")

    ficheiros_origem = obter_lista_ficheiros_recursivo(origem)
    ficheiros_destino = obter_lista_ficheiros_recursivo(destino)

    ficheiros_a_copiar = ficheiros_origem - ficheiros_destino
    ficheiros_existentes = []

    if not ficheiros_a_copiar:
        logging.info("✅ Todos os ficheiros da origem já existem no destino. Nada para copiar!")
        return

    for ficheiro in ficheiros_a_copiar:
        if "$RECYCLE.BIN" in ficheiro:
            logging.warning(f"⚠️ Ignorado: {ficheiro} (pasta protegida)")
            continue

        caminho_origem = os.path.join(origem, ficheiro)
        caminho_destino = os.path.join(destino, ficheiro)

        if not os.path.exists(caminho_origem):
            logging.error(f"❌ Ficheiro de origem '{caminho_origem}' não encontrado. A execução será interrompida.")
            sys.exit(1)

        diretoria_destino = os.path.dirname(caminho_destino)
        if not os.path.exists(diretoria_destino):
            os.makedirs(diretoria_destino)
            logging.info(f"📁 Diretoria criada: {diretoria_destino}")

        if os.path.exists(caminho_destino):
            novo_nome = gerar_nome_sem_colisao(destino, ficheiro)
            ficheiros_existentes.append((ficheiro, caminho_destino, novo_nome))
            caminho_destino = os.path.join(destino, novo_nome)

        try:
            shutil.copy2(caminho_origem, caminho_destino)
            logging.info(f"📂 Copiado: {ficheiro} → {caminho_destino}")
        except Exception as e:
            logging.error(f"❌ Erro ao copiar '{ficheiro}': {e}. A execução será interrompida.")
            sys.exit(1)

    if ficheiros_existentes:
        guardar_lista_em_ficheiro(ficheiros_existentes, destino)

    logging.info("🚀 Processo concluído! Apenas ficheiros novos foram copiados.")

def guardar_lista_em_ficheiro(lista, destino):
    """Guarda num ficheiro os ficheiros que foram renomeados."""
    if not lista:
        return

    caminho_ficheiro = os.path.join(destino, "ficheiros_existentes.txt")
    logging.info(f"💾 Guardando lista de ficheiros renomeados em: {caminho_ficheiro}")

    try:
        with open(caminho_ficheiro, 'w', encoding='utf-8') as f:
            f.write("Ficheiros que já existiam e foram renomeados:\n\n")
            for nome_original, caminho_existente, nome_novo in lista:
                f.write(f"{nome_original} já existia em {caminho_existente} → renomeado para: {nome_novo}\n")

        logging.info(f"📄 Lista de renomeações guardada em: {caminho_ficheiro}")
    except Exception as e:
        logging.error(f"❌ Erro ao guardar lista de renomeações: {e}. A execução será interrompida.")
        sys.exit(1)

# Carregar configuração do ficheiro JSON
config = carregar_configuracao("config.json")

if config:
    origem = config.get("origem")
    destino = config.get("destino")

    if origem and destino:
        copiar_diferencas(origem, destino)
    else:
        logging.error("❌ Configuração inválida! A execução será interrompida.")
        sys.exit(1)
