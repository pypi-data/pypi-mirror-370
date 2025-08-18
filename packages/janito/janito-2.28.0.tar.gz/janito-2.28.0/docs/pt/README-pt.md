# Janito - Controle seu Contexto

[![PyPI version](https://badge.fury.io/py/janito.svg)](https://badge.fury.io/py/janito)

Janito é uma ferramenta de linha de comando (CLI) para gerenciar e interagir com provedores de Modelos de Linguagem de Grande Escala (LLM). Permite configurar chaves de API, selecionar provedores e modelos, e enviar prompts para vários LLMs diretamente do seu terminal. Janito foi projetado para ser extensível, suportando múltiplos provedores e uma ampla variedade de ferramentas para automação e produtividade.

## ✨ Recursos

- 🔑 Gerencie chaves de API e configurações de provedores
- 🤖 Interaja com múltiplos provedores de LLM (OpenAI, Google Gemini, DeepSeek, e mais)
- 🛠️ Liste e use uma variedade de ferramentas registradas
- 📝 Envie prompts e receba respostas diretamente da CLI
- 📋 Liste modelos disponíveis para cada provedor
- 🧩 Arquitetura extensível para adicionar novos provedores e ferramentas
- 🎛️ Saída rica no terminal e registro de eventos

### Recursos Avançados e Arquiteturais

- ⚡ **Arquitetura orientada a eventos**: Sistema modular e desacoplado usando EventBus personalizado para extensibilidade e integração
- 🧑‍💻 **Registro de ferramentas & execução dinâmica**: Registre novas ferramentas facilmente, execute-as por nome ou use em pipelines de automação
- 🤖 **Automação de Agente LLM**: Suporta fluxos de trabalho tipo agente com capacidade de encadear ferramentas ou tomar decisões durante conversas LLM
- 🏗️ **Gerenciamento extensível de provedores**: Adicione, configure ou alterne entre provedores LLM e seus modelos dinamicamente
- 🧰 **Ecossistema rico de ferramentas**: Inclui operações de arquivo, execução de scripts/comandos locais/remotos, processamento de texto e acesso à internet (busca de URLs), todos reutilizáveis por LLM ou usuário
- 📝 **Relatórios abrangentes de eventos & histórico**: Logs detalhados de prompts, eventos, uso de ferramentas e respostas para rastreabilidade e auditoria
- 🖥️ **Interface de terminal aprimorada**: Saídas coloridas e informativas em tempo real para melhorar produtividade e visibilidade durante uso LLM

## 📦 Instalação

Janito é um pacote Python. Como esta é uma versão de desenvolvimento, você pode instalá-lo diretamente do GitHub:

```bash
pip install git+https://github.com/ikignosis/janito.git
```

### Primeira execução e configuração rápida

Janito se integra com provedores LLM externos (lista abaixo), e a maioria deles requer uma assinatura para obter uma API_KEY.

> [!NOTE]
> Atualmente, em 26 de junho de 2025, o Google tem um plano gratuito para seus modelos Gemini-2.5-flash e Gemini-2.5-pro. Apesar das limitações dos modelos e do limite de taxa do plano gratuito, eles podem ser usados para testar o Janito. A API_KEY para Gemini está disponível [aqui](https://aistudio.google.com/app/apikey).

> [!NOTE]
> [Aqui](https://github.com/cheahjs/free-llm-api-resources/blob/main/README.md) uma lista de vários serviços que fornecem acesso gratuito ou créditos para uso de API LLM. Note que nem todos são suportados pelo Janito ainda.

Para uso rápido você pode:

1. Depois de obter a API_KEY do seu provedor LLM favorito, configure a API_KEY no Janito:

```bash
janito --set-api-key SUA_API_KEY -p PROVEDOR
```

2. Depois execute o janito da linha de comando com o provedor LLM específico de sua escolha:

```bash
janito -p PROVEDOR "Olá, quem é você? Como pode me ajudar nas minhas tarefas?"
```

3. ou você pode executar o janito em modo interativo sem o argumento final:

```bash
janito -p PROVEDOR
```

4. se quiser configurar um provedor específico para futuras interações, use:

```bash
janito --set provider=PROVEDOR
```

> [!WARNING]
> Atualmente os provedores suportados são: `openai`, `google`, `anthropic`, `azure_openai`. Você pode obter mais detalhes com `janito --list-providers`.

5. para configuração mais avançada, continue lendo.

## 🚀 Uso

Após a instalação, use o comando `janito` no seu terminal com a sintaxe: `janito [opções] [prompt]`

Janito suporta assistência de uso geral e especializada através do uso de **perfis**. Perfis permitem selecionar um modelo de prompt de sistema específico e comportamento para o agente, permitindo fluxos de trabalho adaptados para diferentes papéis ou tarefas (ex: desenvolvedor, escritor, analista de dados), ou usar o Janito como assistente genérico de IA.

### Perfis: Assistência de Uso Geral e Especializada

- Por padrão, o Janito atua como assistente de uso geral.
- Você pode selecionar um perfil especializado usando a opção `--profile`:
  ```bash
  janito --profile developer "Refatore este código para melhor legibilidade."
  janito --profile writer "Redija um post de blog sobre IA na saúde."
  ```
- Perfis alteram o prompt do sistema e comportamento do agente para se adequar ao papel ou fluxo de trabalho selecionado.
- Para ver perfis disponíveis ou personalizá-los, consulte a documentação ou o diretório `agent/templates/profiles/`.

> **Dica:** Use `--profile` para fluxos de trabalho direcionados, ou omita para um assistente de uso geral.

Janito tem opções de configuração, como `--set api-key API_KEY` e `--set provider=PROVEDOR`, que criam configurações duráveis e opções de uso único, como `-p PROVEDOR` e `-m MODELO`, que estão ativas para uma única execução do comando ou sessão.

### Comandos Básicos

- **Definir Chave de API para um Provedor (requer -p PROVEDOR)**
  ```bash
  janito --set-api-key API_KEY -p PROVEDOR
  ```
  > **Nota:** O argumento `-p PROVEDOR` é obrigatório ao definir uma chave de API. Por exemplo:
  > ```bash
  > janito --set-api-key sk-xxxxxxx -p openai
  > ```

- **Definir o Provedor (durável)**
  ```bash
  janito --set provider=nome_provedor
  ```

- **Listar Provedores Suportados**
  ```bash
  janito --list-providers
  ```

- **Listar Ferramentas Registradas**
  ```bash
  janito --list-tools
  ```

- **Listar Modelos para um Provedor**
  ```bash
  janito -p PROVEDOR --list-models
  ```

- **Enviar um Prompt**
  ```bash
  janito "Qual é a capital da França?"
  ```

- **Iniciar Shell de Chat Interativo**
  ```bash
  janito
  ```

### Opções Avançadas

- **Habilitar Ferramentas de Execução (Execução de Código/Shell)**
  
  Por padrão, **todos os privilégios de ferramentas (ler, escrever, executar)** estão desabilitados por segurança. Isso significa que o Janito inicia sem permissões para executar ferramentas que leem, escrevem ou executam comandos de código/shell a menos que você as habilite explicitamente.

- Para habilitar ferramentas de **leitura** (ex: leitura de arquivo, busca): adicione `-r` ou `--read`
- Para habilitar ferramentas de **escrita** (ex: edição de arquivo): adicione `-w` ou `--write`
- Para habilitar ferramentas de **execução** (execução de código/shell): adicione `-x` ou `--exec`

Você pode combinar esses flags conforme necessário. Por exemplo, para habilitar ambas as ferramentas de leitura e escrita:

```bash
janito -r -w "Leia e atualize este arquivo: ..."
```

Para habilitar todas as permissões (ler, escrever, executar):

```bash
janito -r -w -x "Execute este código: print('Olá, mundo!')"
```

> **Aviso:** Habilitar ferramentas de execução permite executar código ou comandos shell arbitrários. Use `--exec` apenas se confiar em seu prompt e ambiente.

- **Definir um Prompt de Sistema**
  ```bash
  janito -s caminho/para/prompt_sistema.txt "Seu prompt aqui"
  ```

- **Selecionar Modelo e Provedor Temporariamente**
  ```bash
  janito -p openai -m gpt-3.5-turbo "Seu prompt aqui"
  janito -p google -m gemini-2.5-flash "Seu prompt aqui"
  ```

- **Habilitar Registro de Eventos**
  ```bash
  janito -e "Seu prompt aqui"
  ```

## 🌟 Referência de Opções CLI

### Opções CLI Principais
| Opção                  | Descrição                                                                 |
|------------------------|---------------------------------------------------------------------------|
| `--version`            | Mostra a versão do programa                                               |
| `--list-tools`         | Lista todas as ferramentas registradas                                    |
| `--list-providers`     | Lista todos os provedores LLM suportados                                  |
| `-l`, `--list-models`  | Lista modelos para provedor atual/selecionado                             |
| `--set-api-key`        | Define chave de API para um provedor. **Requer** `-p PROVEDOR` para especificar o provedor. |
| `--set provider=nome`  | Define o provedor LLM atual (ex: `janito --set provider=openai`)          |
| `--set PROVEDOR.model=MODELO` ou `--set model=MODELO` | Define o modelo padrão para o provedor atual/selecionado, ou globalmente. (ex: `janito --set openai.model=gpt-3.5-turbo`) |
| `-s`, `--system`       | Define um prompt de sistema (ex: `janito -s caminho/para/prompt_sistema.txt "Seu prompt aqui"`) |

| `-p`, `--provider`     | Seleciona provedor LLM (substitui configuração) (ex: `janito -p openai "Seu prompt aqui"`) |
| `-m`, `--model`        | Seleciona modelo para o provedor (ex: `janito -m gpt-3.5-turbo "Seu prompt aqui"`) |
| `-v`, `--verbose`      | Imprime informações extras antes de responder                               |
| `-R`, `--raw`          | Imprime resposta JSON bruta da API                                          |
| `-e`, `--event-log`    | Registra eventos no console conforme ocorrem                                |
| `prompt`        | Prompt para enviar no modo não interativo (ex. `janito "Qual é a capital da França?"`) |

### 🧩 Comandos do Modo de Chat Estendido
Uma vez dentro do modo de chat interativo, você pode usar estes comandos com barra:

#### 📲 Interação Básica
| Comando           | Descrição                                  |
|-------------------|----------------------------------------------|
| `/exit` ou `exit` | Sai do modo de chat                          |
| `/help`           | Mostra comandos disponíveis                  |
| `/multi`          | Ativa modo de entrada multilinha             |
| `/clear`          | Limpa a tela do terminal                     |
| `/history`        | Mostra histórico de entrada                  |
| `/view`           | Imprime histórico da conversa atual          |
| `/track`          | Mostra histórico de uso de ferramentas       |

#### 💬 Gerenciamento de Conversa
| Comando             | Descrição                                  |
|---------------------|----------------------------------------------|
| `/restart`          | Inicia nova conversa (redefine contexto)     |
| `/prompt`           | Mostra o prompt de sistema atual             |
| `/role <descrição>` | Altera o papel do sistema                    |
| `/lang [código]`    | Altera idioma da interface (ex: `/lang pt`)  |

#### 🛠️ Interação com Ferramentas & Provedores
| Comando              | Descrição                                  |
|----------------------|----------------------------------------------|
| `/tools`             | Lista ferramentas disponíveis              |
| `/-status`           | Mostra status do servidor                  |
| `/-logs`             | Mostra últimas linhas de logs              |
| `/write [on\|off]`   | Habilita ou desabilita permissões de escrita |
| `/read [on\|off]`    | Habilita ou desabilita permissões de leitura |
| `/execute [on\|off]` | Habilita ou desabilita permissões de execução |

#### 📊 Controle de Saída
| Comando             | Descrição                                  |
|---------------------|----------------------------------------------|
| `/verbose`          | Mostra status do modo verbose atual          |
| `/verbose [on\|off]` | Define modo verbose                          |

## Estendendo o Janito

Janito foi construído para ser extensível. Você pode adicionar novos provedores LLM ou ferramentas implementando novos módulos nos diretórios `janito/providers` ou `janito/tools`, respectivamente. Veja o código fonte e documentação do desenvolvedor para mais detalhes.

## Provedores Suportados

- OpenAI
- OpenAI via Azure
- Google Gemini
- DeepSeek
- Anthropic

Veja [supported-providers-models.md](../supported-providers-models.md) para mais detalhes.

## Contribuindo

Contribuições são bem-vindas! Por favor veja o `CONTRIBUTING.md` (se disponível) ou abra uma issue para começar.

---

## Documentação do Desenvolvedor

Para configuração específica do desenvolvedor, versionamento e diretrizes de contribuição, veja [README-dev.md](https://github.com/ikignosis/janito/blob/main/README-dev.md).

## Licença

Este projeto é licenciado sob os termos da licença MIT.

Para mais informações, veja a documentação no diretório `docs/` ou execute `janito --help`.

---

# Suporte

## 📖 Documentação Detalhada

Documentação completa e atualizada está disponível em: https://ikignosis.github.io/janito/

---

## FAQ: Configurando Chaves de API

- [Configuração de múltiplas API_KEYs](#faq-multiplas-api-key)
- [Usar um modelo específico](#faq-usar-modelo-especifico)
- [Buscar provedores LLM disponíveis](#faq-buscar-provedores)
- [Buscar modelos disponíveis](#faq-buscar-modelos)

<a id="faq-multiplas-api-key"></a>
### Configuração de múltiplas API_KEYs

Para definir uma chave de API para um provedor, você **deve** especificar tanto a chave de API quanto o nome do provedor:

```bash
janito --set-api-key SUA_API_KEY -p NOME_PROVEDOR
```

Você pode ter uma API_KEY para cada provedor LLM

```bash
janito --set-api-key API_KEY_1 -p PROVEDOR_1
janito --set-api-key API_KEY_2 -p PROVEDOR_2
```

Depois você pode facilmente usar um provedor ou outro sem mudar a API_KEY

```bash
janito -p PROVEDOR_1 "Qual provedor você usa?"
janito -p PROVEDOR_2 "Qual provedor você usa?"
```

Se omitir o argumento `-p NOME_PROVEDOR`, o Janito mostrará um erro e não definirá a chave.

<a id="faq-usar-modelo-especifico"></a>
### Usar um modelo específico

Para usar um modelo específico, você pode usar a opção `-m` da seguinte forma:

```bash
janito -m gpt-4.1-nano -p openai "Qual modelo você usa?"
```

Ou você pode usar a opção durável `--set`:

```bash
janito --set provider=openai 
janito --set model=gpt-4.1-nano
janito "Qual modelo você usa?"
```

<a id="faq-buscar-provedores"></a>
### Buscar os provedores LLM disponíveis

Você pode listar todos os provedores LLM disponíveis usando:

```bash
janito --list-providers
```

<a id="faq-buscar-modelos"></a>
### Buscar os modelos disponíveis

Cada provedor LLM tem seus próprios modelos, a melhor forma de verificar quais são os modelos disponíveis é usando os seguintes comandos:

```bash
janito -p openai --list-models
janito -p google --list-models
janito -p azure_openai --list-models
janito -p anthropic --list-models
janito -p deepseek --list-models
```

## Pergunte-me Qualquer Coisa

<div align="center">
  <a href="https://github.com/ikignosis/janito.git" title="Pergunte-me Qualquer Coisa">
    <img width="250" src="../imgs/ama.png" alt="Pergunte-me Qualquer Coisa">
  </a>
</div>

Quando as FAQ não forem suficientes, você pode entrar em contato com os contribuidores do projeto fazendo perguntas diretas

<p align="center">
  <kbd><a href="https://github.com/ikignosis/janito/issues/new?labels=question">Faça uma pergunta</a></kbd> <kbd><a href="https://github.com/ikignosis/janito/issues?q=is%3Aissue+is%3Aclosed+label%3Aquestion">Leia perguntas</a></kbd>
</p>

#### Diretrizes

- :mag: Certifique-se de que sua pergunta ainda não foi respondida
- :memo: Use um título e descrição sucintos
- :bug: Bugs & solicitações de recursos devem ser abertos no rastreador de issues relevante
- :signal_strength: Questões de suporte são melhor feitas no Stack Overflow
- :blush: Seja legal, civil e educado
- :heart_eyes: Se você incluir pelo menos um emoji em sua pergunta, o feedback provavelmente virá mais rápido
- [Leia mais AMAs](https://github.com/sindresorhus/amas)
- [O que é AMA?](https://en.wikipedia.org/wiki/R/IAmA)