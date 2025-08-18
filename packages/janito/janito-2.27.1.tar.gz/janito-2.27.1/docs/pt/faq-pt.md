# FAQ - Perguntas Frequentes (Português)

Respostas para as perguntas mais comuns sobre o Janito em português.

## 🚀 Instalação e Configuração

### Como instalo o Janito?

```bash
# Método mais simples
pip install git+https://github.com/ikignosis/janito.git

# Verificar instalação
janito --version
```

### Qual versão do Python preciso?

- **Mínimo:** Python 3.8
- **Recomendado:** Python 3.10 ou superior

### Como obtenho uma chave de API gratuita?

**Google Gemini (Recomendado):**
1. Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Use sem custo com limitações

### Como configuro minha primeira chave?

```bash
# Para Google Gemini (gratuito)
janito --set-api-key SUA_CHAVE_AQUI -p google

# Testar
janito -p google "Qual é a capital do Brasil?"
```

## 🔧 Problemas Comuns

### "janito: command not found"

**Soluções:**
1. **Verificar PATH:**
   ```bash
   python -m janito --version
   ```

2. **Linux/Mac:**
   ```bash
   ~/.local/bin/janito --version
   ```

3. **Windows:**
   ```cmd
   %USERPROFILE%\AppData\Roaming\Python\Python311\Scripts\janito.exe --version
   ```

### "API key not found" ou "Invalid API key"

**Verificar:**
1. **Sintaxe correta:**
   ```bash
   janito --set-api-key SUA_CHAVE -p NOME_PROVEDOR
   ```

2. **Provedor correto:**
   ```bash
   janito --list-providers
   ```

3. **Chave ativa:** Verifique no site do provedor

### "Model not found"

**Solução:**
```bash
# Listar modelos disponíveis
janito -p SEU_PROVEDOR --list-models

# Exemplo com Google
janito -p google --list-models
```

### Erro de SSL/TLS

**Solução temporária:**
```bash
pip install --upgrade certifi
```

## 💰 Custos e Limitações

### Quanto custa usar o Janito?

**O Janito é gratuito!** Mas você paga pelos provedores:

- **Google Gemini:** Plano gratuito disponível
- **OpenAI:** Pago por uso (créditos)
- **Anthropic:** Pago por uso
- **DeepSeek:** Preços competitivos

### Limites do Google Gemini gratuito:
- **Taxa de requisições:** 15 RPM (requests per minute)
- **Tokens por dia:** 1.500.000 tokens
- **Tokens por minuto:** 60.000 tokens

### Como monitorar meu uso?

```bash
# Ativar logs detalhados
janito -e "seu prompt"

# Logs salvos em:
# Linux/Mac: ~/.janito/logs/
# Windows: %USERPROFILE%\.janito\logs\
```

## 🛠️ Uso Diário

### Como alternar entre provedores?

```bash
# Configurar múltiplas chaves
janito --set-api-key CHAVE1 -p google
janito --set-api-key CHAVE2 -p openai

# Alternar facilmente
janito -p google "Usando Google"
janito -p openai "Usando OpenAI"
```

### Como usar em scripts?

```bash
#!/bin/bash
# script.sh
janito -p google "Analise: $1"

# Uso
./script.sh "este arquivo"
```

### Como habilitar/desabilitar ferramentas?

```bash
# Modo único
janito -r -w -x "Execute código"

# Modo interativo
janito
# Dentro do chat: /read on, /write on, /execute on
```

## 🎯 Perfis e Casos de Uso

### O que são perfis?

Perfis são configurações pré-definidas para diferentes tipos de tarefas:

- **developer:** Focado em código e desenvolvimento
- **writer:** Focado em criação de conteúdo
- **analyst:** Focado em análise de dados

### Como uso perfis?

```bash
# Com perfil específico
janito --profile developer "Refatore este código"
janito --profile writer "Crie um blog post"
```

## 🔍 Debugging

### Como ver logs detalhados?

```bash
# Ativar modo verbose
janito -v "seu prompt"

# Ativar registro de eventos
janito -e "seu prompt"

# Ver resposta bruta da API
janito -R "seu prompt"
```

### Como ver minhas configurações?

```bash
# Ver configurações atuais
janito --set provider
janito --set model

# Ver arquivo de configuração
# Linux/Mac: cat ~/.janito/config.json
# Windows: type %USERPROFILE%\.janito\config.json
```

## 🌐 Provedores Suportados

### Lista atual de provedores:
- ✅ **google** - Google Gemini
- ✅ **openai** - OpenAI GPT
- ✅ **anthropic** - Claude
- ✅ **azure_openai** - OpenAI via Azure
- ✅ **deepseek** - DeepSeek

### Como verificar?
```bash
janito --list-providers
```

## 📱 Integrações

### Funciona no Windows?
**Sim!** Janito é multiplataforma:
- Windows (PowerShell, CMD)
- Linux (bash, zsh)
- macOS (bash, zsh)

### Funciona com WSL?
**Sim!** Funciona perfeitamente no WSL:
```bash
# No WSL
pip install git+https://github.com/ikignosis/janito.git
janito --version
```

### Posso usar com VS Code?
**Sim!** Use o terminal integrado:
1. Abra terminal no VS Code
2. Instale o Janito
3. Use normalmente

## 🚀 Dicas Avançadas

### Como criar atalhos?

**Linux/Mac (bash/zsh):**
```bash
# Adicionar ao ~/.bashrc ou ~/.zshrc
echo 'alias j="janito"' >> ~/.bashrc
echo 'alias jg="janito -p google"' >> ~/.bashrc
source ~/.bashrc
```

**Windows (PowerShell):**
```powershell
# Adicionar ao perfil PowerShell
Set-Alias j janito
Set-Alias jg "janito -p google"
```

### Como automatizar tarefas?

```bash
# Script diário
#!/bin/bash
# daily-summary.sh
janito -p google "Resuma as notícias de tecnologia de hoje"

# Agendar com cron (Linux/Mac)
0 9 * * * /caminho/daily-summary.sh
```

## ❓ Perguntas Específicas

### Posso usar offline?
**Não.** Janito requer conexão com provedores LLM online.

### Tem limite de uso?
**Depende do provedor:**
- Google: Limites generosos no plano gratuito
- OpenAI: Limites baseados em créditos
- Outros: Consulte documentação do provedor

### Posso usar meu próprio modelo local?
**Ainda não.** Janito foca em provedores externos.

### Como contribuir?
1. Fork o repositório
2. Faça suas melhorias
3. Envie Pull Request
4. Documente em português!

## 📞 Suporte

### Onde obter ajuda?

1. **Primeiro:** Leia este FAQ
2. **Issues:** [GitHub Issues](https://github.com/ikignosis/janito/issues)
3. **Discussions:** [GitHub Discussions](https://github.com/ikignosis/janito/discussions)
4. **Documentação:** [Docs em Português](./README.md)

### Como reportar bugs?

```bash
# Inclua estas informações:
1. Sistema operacional
2. Versão do Python
3. Versão do Janito
4. Comando usado
5. Mensagem de erro completa
```

### Como sugerir melhorias?

Abra uma issue com:
- Descrição clara da melhoria
- Caso de uso
- Exemplo de como seria útil

---

**Ainda tem dúvidas?** Abra uma [issue](https://github.com/ikignosis/janito/issues) com sua pergunta!