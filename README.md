# n8n-local-sync

Uma ferramenta CLI open source para **versionar, validar, exportar, importar e sincronizar workflows de instâncias n8n self-hosted/local utilizando Git**.

## O que é

`n8n-local-sync` é uma ferramenta instalável independentemente (via `pipx` ou `pip`) projetada para ajudar desenvolvedores a versionar e compartilhar workflows do n8n de forma organizada, minimizando os conflitos de JSON e mantendo um repositório Git como a fonte da verdade.

## Problema

O n8n permite exportar workflows através da UI ou CLI, mas equipes que utilizam o n8n localmente precisam de uma forma estruturada de:
* manter workflows no Git;
* compartilhar alterações entre desenvolvedores;
* validar workflows antes de realizar commits;
* reproduzir um ambiente n8n a partir do Git;
* evitar importações manuais tediosas e propensas a erros.

## Como funciona

A ferramenta atua como uma ponte entre o repositório Git e a instância n8n local ou remota. Uma vez inicializada em um projeto, a ferramenta gerencia um diretório de workflows (por padrão, `n8n/workflows/`) e comunica-se com a REST API do n8n (ou outros mecanismos suportados) para sincronizar o estado.

## Arquitetura

O `n8n-local-sync` utiliza uma abordagem desacoplada:
* A ferramenta é independente do ambiente n8n em si.
* A configuração é guardada em um arquivo local do projeto (`.n8n-sync.yaml`).
* Utiliza a REST API oficial do n8n para comunicação estável.

## Instalação via PyPI

Para uso geral em seus projetos, instale através do `pipx`:

```bash
pipx install n8n-local-sync
```

## Instalação via GitHub

Para instalar a versão mais recente diretamente do repositório:

```bash
pipx install git+https://github.com/<owner>/n8n-local-sync.git
```

## Desenvolvimento Local

```bash
git clone https://github.com/<owner>/n8n-local-sync.git
cd n8n-local-sync
pip install -e .
```

## Quick Start

```bash
cd meu-projeto
n8n-sync init
n8n-sync validate
n8n-sync sync
```

## Fluxo de Desenvolvimento Típico

1. `git pull`
2. `n8n-sync sync`
3. (Editar fluxos no UI do n8n)
4. `n8n-sync export`
5. `n8n-sync validate`
6. `git diff`
7. `git commit`
8. `git push`

## Configuração

O projeto depende de um arquivo `.n8n-sync.yaml` na raiz do seu projeto. A ferramenta criará este arquivo para você durante a execução do comando `init`.

## Credenciais

**Atenção:** Workflows e credenciais são conceitos diferentes. Os workflows são versionados por esta ferramenta, mas credenciais NÃO devem ser versionadas em hipótese alguma (API keys, passwords, tokens, etc.).

## Limitações

A primeira versão foca na sincronização básica de workflows localizados e versionáveis no Git, sem incluir gestão de usuários, secrets, variáveis de ambiente ou deployments complexos.

## Licença

MIT
