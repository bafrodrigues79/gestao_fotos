
# 🗂️ Organizador de Ficheiros por Data

Este script Python copia ficheiros de uma pasta de origem para uma pasta de destino, organizando-os automaticamente por ano e mês com base na data de modificação. Ele evita sobrescrever ficheiros existentes renomeando-os quando necessário.

## 📦 Funcionalidades

- Organiza ficheiros por estrutura de diretórios `ano/mês`.
- Suporte para meses em **português**.
- Evita sobrescrever ficheiros com nomes duplicados.
- Gera log com os ficheiros renomeados.
- Totalmente configurável via ficheiro `config.json`.

## 🛠️ Requisitos

- Python 3.6+
- Sistema de ficheiros compatível com caminhos longos (Windows/Linux/macOS)

## 📁 Estrutura do Projeto

```
📂 projeto
├── main.py
├── config.json
└── ficheiros_existentes_YYYY-MM-DD_HH-MM-SS.txt
```

## ⚙️ Configuração

Crie um ficheiro `config.json` no mesmo diretório com o seguinte conteúdo:

```json
{
  "origem": "caminho/para/origem",
  "destino": "caminho/para/destino"
}
```

## 🚀 Como Usar

1. Clone ou copie o projeto.
2. Atualize o `config.json` com os caminhos desejados.
3. Execute o script:

```bash
python main.py
```

4. Verifique os ficheiros copiados e, se houver renomeações, veja o ficheiro de log gerado no diretório de destino.

## 📄 Exemplo de Log

```txt
Ficheiros que já existiam e foram renomeados:

imagem.png já existia em: destino/2024/10_Outubro → renomeado para: imagem(1).png
```

## 🧪 Testado em

- ✅ Windows 10
- ✅ macOS Ventura
- ✅ Ubuntu 22.04

## 📌 Notas

- A data de organização baseia-se na **data de modificação** do ficheiro.
- O script ignora subdiretórios não acessíveis ou protegidos.

## 📃 Licença

MIT License
