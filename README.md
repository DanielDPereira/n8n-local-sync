# n8n-local-sync

Uma ferramenta CLI open source e focada no desenvolvedor para **versionar, validar, exportar, importar e sincronizar workflows de instâncias n8n self-hosted/local utilizando Git**.

## O que é

`n8n-local-sync` é uma ferramenta de linha de comando (instalável via `pipx` ou `pip`) projetada para ajudar desenvolvedores a gerenciar workflows do n8n de forma organizada, garantindo que o repositório Git atue como a **verdadeira fonte da verdade**.

## Principais Funcionalidades

- **Sincronização Bidirecional**: Importe fluxos do repositório para o n8n ou exporte fluxos do n8n para o repositório (`sync`, `import`, `export`).
- **Validação Automática**: Verifica a sanidade e ausência de credenciais embutidas acidentalmente nos JSONs (`validate`).
- **Suporte Multi-Ambiente**: Compatível com múltiplos ambientes, suportando URLs configuráveis (`N8N_BASE_URL`).
- **Modo Dry-Run (Simulação)**: Visualize exatamente quais fluxos serão criados ou atualizados sem afetar a sua instância n8n (`--dry-run`).
- **Filtro por Tags**: Exporte e organize seus fluxos segmentados por tags de equipe ou projeto (`--tag`).
- **Integração Pre-commit**: Gancho de pré-commit pronto para bloquear *commits* de fluxos defeituosos na origem.

## Instalação via PyPI

A maneira recomendada de utilizar globalmente a ferramenta:

```bash
pipx install n8n-local-sync
```

*(O suporte à publicação contínua no PyPI está integrado no repositório!)*

## Instalação via GitHub

Para instalar a versão de ponta diretamente do repositório:

```bash
pipx install git+https://github.com/DanielDPereira/n8n-local-sync.git
```

## Configuração do Ambiente (Variáveis)

O `n8n-local-sync` depende das seguintes variáveis de ambiente, que devem ser exportadas no seu terminal ou colocadas em um arquivo `.env` na raiz do seu projeto:

- `N8N_API_KEY` **(Obrigatório)**: Uma chave de API REST válida da sua instância n8n (gerada em *Settings > n8n API*).
- `N8N_BASE_URL` *(Opcional)*: A URL raiz da sua instância n8n. O padrão é `http://localhost:5678`. Para conectar-se à produção, basta definir `N8N_BASE_URL=https://n8n.sua-empresa.com`.

## Quick Start (Guia Rápido)

```bash
cd meu-projeto

# 1. Inicializa o arquivo de configuração local (.n8n-sync.yaml) e a pasta de workflows
n8n-sync init

# 2. Faz o pull do n8n (importação bidirecional dos fluxos)
n8n-sync sync

# 3. Verifica alterações pendentes (Local vs n8n)
n8n-sync status
n8n-sync diff
```

## Comandos Avançados

### Exportação Direcionada e Tags

Você pode exportar workflows segmentados baseados nas Tags que estão configuradas na sua interface n8n:
```bash
n8n-sync export --tag "production"
```

### Dry-Run (Modo de Simulação)

Antes de rodar a sincronização, veja o que aconteceria:
```bash
n8n-sync sync --dry-run
n8n-sync import --dry-run
```

## Integração com Pre-commit

O `n8n-local-sync` atua perfeitamente como um hook de pre-commit para proteger seu repositório. Para usá-lo, crie ou atualize o `.pre-commit-config.yaml` no seu repositório cliente:

```yaml
repos:
  - repo: https://github.com/DanielDPereira/n8n-local-sync
    rev: v1.0.0  # substitua pela release desejada
    hooks:
      - id: n8n-sync-validate
```

## Fluxo de Desenvolvimento Típico em Equipe

1. `git pull`
2. `n8n-sync sync`
3. (Editar fluxos no UI do n8n)
4. `n8n-sync export`
5. `n8n-sync validate` (Opcional, se o pre-commit não estiver habilitado)
6. `git diff`
7. `git commit`
8. `git push`

## Credenciais

**Atenção:** Workflows e credenciais são conceitos diferentes. Os workflows são versionados por esta ferramenta, mas credenciais NÃO devem ser versionadas em hipótese alguma. O comando `validate` procura e bloqueia hardcodes identificáveis.

## Licença

MIT
