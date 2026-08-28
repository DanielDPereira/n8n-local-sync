# Instruções para Agentes de IA

Este documento (AGENTS.md) fornece diretrizes fundamentais para qualquer Agente de IA que venha a interagir com, dar manutenção ou expandir o código deste repositório.

## 1. Objetivo e Escopo

O `n8n-local-sync` é uma ferramenta CLI (Command Line Interface) open source.
* **Propósito:** Versionar, validar, exportar, importar e sincronizar workflows de n8n.
* **Não é:** Um servidor, uma aplicação web, ou um sistema distribuído complexo. Não faça overengineering.
* **Foco Inicial:** Interface CLI simples em Python que interaja com o Git e instâncias n8n.

## 2. Arquitetura e Integração com n8n

* O `n8n-local-sync` é uma ferramenta externa e independente. Não a embuta dentro da stack Docker do n8n de forma intrusiva (como um sidecar obrigatório).
* **Comunicação com n8n:** **Antes de utilizar qualquer comando, API, parâmetro ou comportamento específico do n8n, consulte a documentação oficial correspondente à versão fixada.** Utilize preferencialmente a **Public REST API** do n8n (introduzida na versão 0.164.0+) como meio de exportar/importar workflows, requerendo a passagem de API Keys (via `.env`), ao invés de hacks usando a CLI legada local.
* **Fonte da Verdade:** O Git (arquivos `.json` no repositório) é a única fonte da verdade. O banco de dados do n8n é considerado efêmero em relação aos workflows gerenciados pela ferramenta.

## 3. Padrões e Convenções de Código

* **Python:** Utilizar `Typer` para a CLI, `Pydantic` e `PyYAML` para as configurações e validações.
* **Scripts Shell:** Quando usar bash para automação ou CI, sempre inicie com `#!/usr/bin/env bash` seguido de `set -euo pipefail`. Use `ShellCheck`! Não use `eval`.
* **Packaging:** Utilize `pyproject.toml` (`hatchling`) para definir metadados do pacote e entrypoints CLI (`n8n-sync`).

## 4. Segurança (Criticamente Importante)

* Nunca adicione lógicas que cometam credenciais ou secrets no repositório.
* Arquivos `.env` devem sempre estar no `.gitignore`.
* A CLI deve alertar se tentar fazer parsing de um `.json` exportado que contenha credenciais embedded.

## 5. Testes e CI

* Python: Utilize `pytest`. Testes unitários para a configuração, parse do JSON e diffing.
* A integração contínua (GitHub Actions) deve rodar o Pytest e lint (Ruff) antes de autorizar publicações no PyPI.

## 6. Alterações na CLI

A CLI é a API primária da ferramenta para o usuário.
* Mantenha os comandos padronizados: `init`, `validate`, `export`, `import`, `sync`, `status`, `diff`.
* **Não invente comandos** que não estão planejados, a não ser que extremamente justificado por um roadmap.
* Garanta códigos de saída (`exit code`) apropriados: `0` para sucesso, não-`0` para erros, o que é fundamental para CI/CD e pre-commit hooks.
