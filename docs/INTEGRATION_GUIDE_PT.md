# Guia de Integração: Usando o n8n-local-sync em qualquer Repositório

Este guia explica como integrar o `n8n-local-sync` aos seus repositórios de projetos n8n existentes (por exemplo, ao lado do seu `docker-compose.yml` ou nós customizados do n8n). Como o `n8n-local-sync` segue princípios padrão de GitOps, ele opera de forma transparente ao lado do seu código existente sem interferir nele.

## Passo 1: Instalar a CLI

Certifique-se de ter o Python 3.9+ instalado no seu sistema. Você deve instalar o `n8n-local-sync` globalmente para poder usar a CLI de qualquer lugar.

```bash
pip install n8n-local-sync
```

*(Dica: Se você prefere isolar ambientes Python, recomendamos o uso de `pipx install n8n-local-sync`).*

## Passo 2: Inicializar o Projeto

Abra seu terminal e navegue até a **raiz do seu repositório** (por exemplo, a mesma pasta onde está localizado o seu arquivo `docker-compose.yml` do n8n).

Execute o comando de inicialização:
```bash
n8n-sync init
```

Isso criará automaticamente:
1. Um diretório `n8n/workflows/` (onde seus workflows em JSON serão salvos).
2. Um arquivo `.n8n-sync.yaml` (sua configuração básica).

## Passo 3: Configurar a Conexão

Abra o arquivo `.n8n-sync.yaml` recém-criado. Verifique se a `url` corresponde à sua instância do n8n. O padrão é `http://localhost:5678`, o que funciona perfeitamente se você estiver executando o n8n via Docker local.

Em seguida, você precisa autorizar a CLI. **Crie um arquivo `.env`** na raiz do seu projeto (se já não existir) e adicione a sua Chave de API do n8n (que você pode gerar nas configurações da interface do n8n):

```env
N8N_API_KEY=sua_chave_de_api_aqui
```

> ⚠️ **Importante:** Certifique-se de que seu arquivo `.env` esteja listado no arquivo `.gitignore` do seu repositório para não vazar acidentalmente sua chave de API no GitHub ou GitLab.

## Passo 4: O Primeiro "Pull" (Baixar os Workflows)

Para baixar todos os workflows existentes da sua instância n8n e salvá-los localmente:

```bash
n8n-sync export
# Alternativamente, você pode usar: n8n-sync pull
```

Este comando preenche a pasta `n8n/workflows/` com arquivos `.json` limpos e normalizados, nomeados com seus respectivos IDs de workflow.

## Passo 5: Salvar no Git

Agora você retorna ao seu fluxo de desenvolvimento padrão. Faça o commit dos novos arquivos para o seu repositório:

```bash
git add .n8n-sync.yaml n8n/workflows/
git commit -m "chore: initial n8n workflow setup"
git push
```

---

## 🔄 Fluxo de Trabalho GitOps Diário

Uma vez integrado, seu processo diário se torna direto.

**Quando você constrói/edita um workflow na interface do n8n (navegador):**
```bash
n8n-sync pull
git add n8n/workflows/
git commit -m "feat: update sales automation workflow"
```

**Quando você baixa (pull) o repositório em outra máquina (ou via CI/CD para deploy):**
```bash
# Envia os workflows versionados no Git local para a instância n8n em execução
n8n-sync push
```

Se várias pessoas editarem o mesmo workflow simultaneamente em ambientes diferentes, o `n8n-local-sync` detectará o `CONFLICT` durante o push ou pull e abortará a operação de forma segura, avisando você antes que qualquer trabalho seja sobrescrito!
