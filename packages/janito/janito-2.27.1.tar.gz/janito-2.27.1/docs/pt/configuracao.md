# Configuração - Janito

Guia completo para configurar provedores, modelos e preferências no Janito.

## 🔑 Configurando Chaves de API

### Google Gemini (Recomendado para Iniciantes)

1. Obtenha sua chave: [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Configure:
```bash
janito --set-api-key SUA_CHAVE_AQUI -p google
```

### OpenAI

1. Obtenha sua chave: [OpenAI Platform](https://platform.openai.com/api-keys)
2. Configure:
```bash
janito --set-api-key sk-sua-chave-aqui -p openai
```

### Anthropic

1. Obtenha sua chave: [Anthropic Console](https://console.anthropic.com/)
2. Configure:
```bash
janito --set-api-key sk-ant-sua-chave-aqui -p anthropic
```

### DeepSeek

1. Obtenha sua chave: [DeepSeek Platform](https://platform.deepseek.com/)
2. Configure:
```bash
janito --set-api-key sk-sua-chave-aqui -p deepseek
```

## ⚙️ Configurações Duráveis vs Temporárias

### Configurações Duráveis (Salvas)

```bash
# Definir provedor padrão
janito --set provider=google

# Definir modelo padrão para um provedor
janito --set google.model=gemini-2.5-flash

# Definir modelo global
janito --set model=gpt-3.5-turbo
```

### Configurações Temporárias (Uso Único)

```bash
# Usar provedor específico apenas uma vez
janito -p openai "Qual modelo você usa?"

# Usar modelo específico apenas uma vez
janito -m gpt-4 "Resposta mais detalhada"

# Combinar ambos
janito -p google -m gemini-2.5-pro "Análise complexa"
```

## 📊 Verificando Configurações Atuais

### Ver Configurações Salvas

```bash
# Ver provedor atual
janito --set provider

# Ver modelo atual
janito --set model

# Ver configurações específicas do provedor
janito --set google.model
janito --set openai.model
```

### Listar Opções Disponíveis

```bash
# Listar todos os provedores
janito --list-providers

# Listar modelos de um provedor específico
janito -p google --list-models
janito -p openai --list-models
janito -p anthropic --list-models
```

## 🎯 Configurações por Provedor

### Google Gemini

```bash
# Modelos comuns:
# - gemini-2.5-flash (gratuito com limitações)
# - gemini-2.5-pro (mais avançado)
# - gemini-1.5-flash (versão anterior)

janito --set provider=google
janito --set google.model=gemini-2.5-flash
```

### OpenAI

```bash
# Modelos comuns:
# - gpt-3.5-turbo (mais econômico)
# - gpt-4 (mais avançado)
# - gpt-4-turbo (balanço custo/desempenho)

janito --set provider=openai
janito --set openai.model=gpt-3.5-turbo
```

### Anthropic

```bash
# Modelos comuns:
# - claude-3-5-sonnet (balanço custo/desempenho)
# - claude-3-opus (mais avançado)
# - claude-3-haiku (mais rápido)

janito --set provider=anthropic
janito --set anthropic.model=claude-3-5-sonnet
```

### DeepSeek

```bash
# Modelos comuns:
# - deepseek-chat (modelo principal)
# - deepseek-coder (especializado em código)

janito --set provider=deepseek
janito --set deepseek.model=deepseek-chat
```

## 🔄 Gerenciando Múltiplas Contas

### Configurando Várias Chaves

```bash
# Configurar chaves para diferentes provedores
janito --set-api-key CHAVE_GOOGLE -p google
janito --set-api-key CHAVE_OPENAI -p openai
janito --set-api-key CHAVE_ANTHROPIC -p anthropic

# Alternar entre provedores facilmente
janito -p google "Usando Google"
janito -p openai "Usando OpenAI"
janito -p anthropic "Usando Anthropic"
```

### Criando Perfis de Uso

```bash
# Configurar provedor para desenvolvimento
janito --set provider=openai
janito --set openai.model=gpt-4

# Configurar provedor para tarefas rápidas
janito --set provider=google
janito --set google.model=gemini-2.5-flash
```

## ⚡ Configurações Avançadas

### Variáveis de Ambiente

Você pode usar variáveis de ambiente para configurações:

```bash
# Linux/Mac
export JANITO_PROVIDER=google
export JANITO_MODEL=gemini-2.5-flash

# Windows
set JANITO_PROVIDER=google
set JANITO_MODEL=gemini-2.5-flash
```

### Arquivo de Configuração

As configurações são salvas em:
- **Linux/Mac:** `~/.janito/config.json`
- **Windows:** `%USERPROFILE%\.janito\config.json`

### Configuração via JSON

```json
{
  "provider": "google",
  "google": {
    "model": "gemini-2.5-flash",
    "api_key": "sua-chave-aqui"
  },
  "openai": {
    "model": "gpt-3.5-turbo",
    "api_key": "sk-sua-chave-aqui"
  }
}
```

## 🛡️ Segurança

### Melhores Práticas

1. **Nunca compartilhe suas chaves de API**
2. **Use variáveis de ambiente para chaves sensíveis**
3. **Revogue chaves comprometidas imediatamente**
4. **Use chaves diferentes para diferentes ambientes**

### Revogando Chaves

```bash
# Remover chave de um provedor
# Simplesmente configure uma nova chave ou remova do arquivo config.json
```

## 🎯 Configurações por Cenário

### Para Desenvolvimento

```bash
# Configuração ideal para desenvolvimento
janito --set provider=openai
janito --set openai.model=gpt-4
janito --set-api-key SUA_CHAVE -p openai
```

### Para Uso Gratuito

```bash
# Configuração para uso gratuito com Google
janito --set provider=google
janito --set google.model=gemini-2.5-flash
janito --set-api-key SUA_CHAVE_GOOGLE -p google
```

### Para Análise de Dados

```bash
# Configuração para análise de dados
janito --set provider=anthropic
janito --set anthropic.model=claude-3-5-sonnet
janito --set-api-key SUA_CHAVE -p anthropic
```

## 🔍 Solução de Problemas

### Erro: "API key not found"

```bash
# Verificar se a chave está configurada
janito --set-api-key SUA_CHAVE -p NOME_PROVEDOR

# Verificar se está usando o provedor correto
janito -p google --list-models
```

### Erro: "Model not found"

```bash
# Listar modelos disponíveis
janito -p SEU_PROVEDOR --list-models

# Verificar ortografia do modelo
janito --set SEU_PROVEDOR.model=MODELO_CORRETO
```

### Erro: "Provider not supported"

```bash
# Listar provedores suportados
janito --list-providers

# Verificar se digitou corretamente
# Use minúsculas: google, openai, anthropic, deepseek
```

## 📋 Checklist de Configuração

- [ ] Python 3.8+ instalado
- [ ] Janito instalado via pip
- [ ] Chave de API obtida do provedor escolhido
- [ ] Chave configurada com `--set-api-key`
- [ ] Provedor configurado com `--set provider`
- [ ] Modelo configurado (se necessário)
- [ ] Teste básico realizado

## 🚀 Próximos Passos

Após configurar:

1. [Guia de Uso](guia-uso.md) - Aprenda comandos básicos
2. [Perfis](perfis.md) - Configure perfis para diferentes tarefas
3. [Ferramentas](ferramentas.md) - Explore ferramentas disponíveis
4. [Exemplos](exemplos.md) - Veja casos de uso práticos