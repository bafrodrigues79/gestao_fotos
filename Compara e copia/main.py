import os
import shutil
import json


def carregar_configuracao(ficheiro_config):
    """Carrega as diretorias do ficheiro config.json."""
    try:
        with open(ficheiro_config, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"❌ Erro ao carregar '{ficheiro_config}'. Verifique o ficheiro.")
        return None


def obter_lista_ficheiros_recursivo(diretorio):
    """Obtém a lista completa de ficheiros, incluindo subpastas."""
    ficheiros = set()
    for root, _, files in os.walk(diretorio):
        for file in files:
            ficheiros.add(os.path.relpath(os.path.join(root, file), diretorio))
    return ficheiros


def gerar_nome_sem_colisao(destino, nome_ficheiro):
    """Gera um novo nome para ficheiros que já existem no destino."""
    base, ext = os.path.splitext(nome_ficheiro)
    contador = 1
    novo_nome = nome_ficheiro

    while os.path.exists(os.path.join(destino, novo_nome)):
        novo_nome = f"{base}({contador}){ext}"
        contador += 1

    return novo_nome


def copiar_diferencas(origem, destino):
    """Compara ficheiros e copia apenas os que não existem no destino, renomeando se necessário."""
    if not os.path.exists(origem):
        print(f"❌ A diretoria de origem '{origem}' não existe.")
        return

    if not os.path.exists(destino):
        os.makedirs(destino)

    ficheiros_origem = obter_lista_ficheiros_recursivo(origem)
    ficheiros_destino = obter_lista_ficheiros_recursivo(destino)

    ficheiros_a_copiar = ficheiros_origem - ficheiros_destino
    ficheiros_existentes = []

    if not ficheiros_a_copiar:
        print("✅ Todos os ficheiros da origem já existem no destino. Nada para copiar!")
        return

    for ficheiro in ficheiros_a_copiar:
        caminho_origem = os.path.join(origem, ficheiro)
        caminho_destino = os.path.join(destino, ficheiro)

        # Criar diretoria caso não exista
        diretoria_destino = os.path.dirname(caminho_destino)
        if not os.path.exists(diretoria_destino):
            os.makedirs(diretoria_destino)

        # Verificar se o ficheiro já existe no destino
        if os.path.exists(caminho_destino):
            novo_nome = gerar_nome_sem_colisao(destino, ficheiro)
            ficheiros_existentes.append((ficheiro, caminho_destino, novo_nome))
            caminho_destino = os.path.join(destino, novo_nome)

        shutil.copy2(caminho_origem, caminho_destino)
        print(f"📂 Copiado: {ficheiro}")

    if ficheiros_existentes:
        guardar_lista_em_ficheiro(ficheiros_existentes, destino)

    print("\n🚀 Processo concluído! Apenas ficheiros novos foram copiados.")


def guardar_lista_em_ficheiro(lista, destino):
    """Guarda num ficheiro os ficheiros que foram renomeados."""
    if not lista:
        return

    caminho_ficheiro = os.path.join(destino, "ficheiros_existentes.txt")
    with open(caminho_ficheiro, 'w', encoding='utf-8') as f:
        f.write("Ficheiros que já existiam e foram renomeados:\n\n")
        for nome_original, caminho_existente, nome_novo in lista:
            f.write(f"{nome_original} já existia em {caminho_existente} → renomeado para: {nome_novo}\n")

    print(f"\n📄 Lista de renomeações guardada em: {caminho_ficheiro}")


# Carregar configuração do ficheiro JSON
config = carregar_configuracao("config.json")

if config:
    origem = config.get("origem")
    destino = config.get("destino")

    if origem and destino:
        copiar_diferencas(origem, destino)
    else:
        print("❌ Configuração inválida! Verifique 'origem' e 'destino' no ficheiro JSON.")
