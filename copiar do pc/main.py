import os
import shutil
import json
from datetime import datetime

MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]


def carregar_configuracao(ficheiro_config):
    with open(ficheiro_config, 'r') as f:
        return json.load(f)


def gerar_nome_sem_colisao(pasta_destino, nome_ficheiro, ficheiros_existentes, nome_final_ref):
    base, ext = os.path.splitext(nome_ficheiro)
    contador = 1
    novo_nome = nome_ficheiro
    while os.path.exists(os.path.join(pasta_destino, novo_nome)):
        if contador == 1:
            ficheiros_existentes.append((nome_ficheiro, os.path.join(pasta_destino, nome_ficheiro), None))
        novo_nome = f"{base}({contador}){ext}"
        contador += 1
    nome_final_ref.append(novo_nome)
    return novo_nome


def copiar_ficheiros_por_data(origem, destino):
    ficheiros_existentes = []

    if not os.path.isdir(origem):
        print(f"Pasta de origem '{origem}' não existe.")
        return ficheiros_existentes

    for root, _, ficheiros in os.walk(origem):
        for nome_ficheiro in ficheiros:
            caminho_origem = os.path.join(root, nome_ficheiro)
            try:
                timestamp = os.path.getmtime(caminho_origem)
                data_mod = datetime.fromtimestamp(timestamp)

                num_mes = data_mod.month
                nome_mes = MESES_PT[num_mes - 1]
                nome_pasta_mes = f"{num_mes}_{nome_mes}"

                pasta_destino = os.path.join(destino, f"{data_mod.year}", nome_pasta_mes)
                os.makedirs(pasta_destino, exist_ok=True)

                nome_final_ref = []
                nome_final = gerar_nome_sem_colisao(pasta_destino, nome_ficheiro, ficheiros_existentes, nome_final_ref)
                caminho_destino = os.path.join(pasta_destino, nome_final)

                shutil.copy2(caminho_origem, caminho_destino)
                print(f"Copiado: {caminho_origem} -> {caminho_destino}")

                # Atualiza com o nome final se foi renomeado
                if nome_ficheiro != nome_final_ref[0]:
                    # Atualiza a tupla para incluir o nome novo
                    ficheiros_existentes[-1] = (nome_ficheiro, os.path.join(pasta_destino, nome_ficheiro),
                                                nome_final_ref[0])

            except Exception as e:
                print(f"Erro ao copiar '{caminho_origem}': {e}")

    return ficheiros_existentes


def guardar_lista_em_ficheiro(lista, destino):
    if not lista:
        return
    try:
        agora = datetime.now()
        timestamp = agora.strftime("%Y-%m-%d_%H-%M-%S")
        nome_ficheiro = f"ficheiros_existentes_{timestamp}.txt"
        caminho_ficheiro = os.path.join(destino, nome_ficheiro)

        with open(caminho_ficheiro, 'w', encoding='utf-8') as f:
            f.write("Ficheiros que já existiam e foram renomeados:\n\n")
            for nome_original, caminho_existente, nome_novo in lista:
                if nome_novo:
                    f.write(f"{nome_original} já existia em: {caminho_existente} → renomeado para: {nome_novo}\n")
                else:
                    f.write(f"{nome_original} já existia em: {caminho_existente}\n")
        print(f"\n📄 Lista guardada em: {caminho_ficheiro}")
    except Exception as e:
        print(f"Erro ao guardar a lista em ficheiro: {e}")


def main():
    config = carregar_configuracao("config.json")
    origem = config.get("origem")
    destino = config.get("destino")

    if not origem or not destino:
        print("Configuração inválida. Verifique 'origem' e 'destino'.")
        return

    ficheiros_existentes = copiar_ficheiros_por_data(origem, destino)

    if ficheiros_existentes:
        print("\n⚠️ Ficheiros que já existiam no destino:")
        for nome_original, caminho_existente, nome_novo in ficheiros_existentes:
            if nome_novo:
                print(f" - {nome_original} já existia em {caminho_existente} → renomeado para: {nome_novo}")
            else:
                print(f" - {nome_original} já existia em {caminho_existente}")
        guardar_lista_em_ficheiro(ficheiros_existentes, destino)
    else:
        print("\n✅ Nenhum ficheiro foi sobrescrito ou renomeado.")


if __name__ == "__main__":
    main()
