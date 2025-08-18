# Guia de Uso - Janito

Este guia irá ensiná-lo a usar o Janito no dia a dia.

## 🎯 Começando

### Modo Interativo (Recomendado para Iniciantes)

```bash
# Iniciar modo interativo
janito

# Ou especificar um provedor
janito -p google
```

No modo interativo, você pode conversar naturalmente com o Janito. Use `/help` para ver comandos disponíveis.

### Modo Único (Execução Direta)

```bash
# Comando simples
janito "Explique o conceito de machine learning"

# Com provedor específico
janito -p openai "Como funciona o GPT-4?"

# Com modelo específico
janito -p google -m gemini-2.5-flash "Traduza 'Hello World' para português"
```

## 💬 Comandos do Modo Interativo

### Comandos Básicos

```bash
# Entrar no modo interativo
janito

# Com provedor específico
janito -p google

# Com perfil específico
janito --profile developer
```

### Comandos Úteis Dentro do Chat

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `/help` | Mostra todos os comandos | `/help` |
| `/exit` | Sai do chat | `/exit` |
| `/clear` | Limpa a tela | `/clear` |
| `/history` | Mostra histórico | `/history` |
| `/tools` | Lista ferramentas disponíveis | `/tools` |
| `/restart` | Reinicia conversa | `/restart` |
| `/lang pt` | Muda idioma para português | `/lang pt` |

### Comandos de Permissão

| Comando | Descrição |
|---------|-----------|
| `/read on` | Habilita leitura de arquivos |
| `/write on` | Habilita escrita de arquivos |
| `/execute on` | Habilita execução de código |
| `/read off` | Desabilita leitura |
| `/write off` | Desabilita escrita |
| `/execute off` | Desabilita execução |

## 🛠️ Exemplos Práticos

### Exemplo 1: Análise de Código

```bash
# Habilitar permissões de leitura e execução
janito -r -x

# Dentro do chat:
"Analise este arquivo Python e sugira melhorias:"
```

### Exemplo 2: Escrita de Documentação

```bash
# Com perfil de escritor
janito --profile writer

# Dentro do chat:
"Crie documentação para uma API REST"
```

### Exemplo 3: Desenvolvimento

```bash
# Com perfil de desenvolvedor e permissões completas
janito --profile developer -r -w -x

# Dentro do chat:
"Crie um script Python para processar CSVs"
```

## 🔧 Dicas de Uso

### 1. Usar Perfis

```bash
# Ver perfis disponíveis (quando implementado)
# Por enquanto, use --profile com nomes como:
janito --profile developer "Refatore este código"
janito --profile writer "Redija um email formal"
janito --profile analyst "Analise estes dados"
```

### 2. Histórico de Comandos

```bash
# Usar setas para cima/baixo para navegar no histórico
# No modo interativo, use /history para ver comandos anteriores
```

### 3. Prompts Eficazes

```bash
# Seja específico
janito "Explique recursão em Python com exemplos"

# Use contexto
janito "Considerando que sou iniciante em Python, explique funções"

# Peça formatos específicos
janito "Liste 5 frameworks Python populares em formato markdown"
```

### 4. Salvando Conversas

```bash
# Ativar registro de eventos para salvar histórico
janito -e

# Os logs são salvos em: ~/.janito/logs/
```

## 🎭 Perfis Comuns

### Desenvolvedor
```bash
janito --profile developer -r -w -x
```
- Focado em código
- Tem acesso a ferramentas de desenvolvimento
- Ajuda com debugging, refactoring, etc.

### Escritor
```bash
janito --profile writer
```
- Focado em criação de conteúdo
- Ajuda com redação, edição, documentação

### Analista
```bash
janito --profile analyst -r
```
- Focado em análise de dados
- Ajuda com interpretação de dados, relatórios

## 🚨 Comandos Importantes

### Verificar Status
```bash
# Ver provedor atual
janito --set provider

# Ver modelo atual
janito --set model

# Listar tudo
janito --list-providers
janito --list-tools
```

### Configurações Rápidas
```bash
# Mudar provedor temporariamente
janito -p openai "Qual modelo você usa?"

# Mudar modelo temporariamente
janito -p google -m gemini-2.5-pro "Resposta detalhada"
```

## 💡 Truques Avançados

### 1. Usar Arquivos como Input

```bash
# Ler prompt de arquivo
janito -s meu_prompt.txt "Execute as instruções"

# Processar arquivo
janito -r "Analise o conteúdo de data.csv"
```

### 2. Pipeline de Comandos

```bash
# Usar com outros comandos do sistema
echo "Explique: $(cat arquivo.txt)" | janito

# Ou no Windows
type arquivo.txt | janito
```

### 3. Scripts de Automação

```bash
# Criar script bash/zsh
#!/bin/bash
janito -p google -r -w "Atualize meu README com base no código"
```

## 📱 Atalhos Úteis

### Linux/Mac
```bash
# Alias no ~/.bashrc ou ~/.zshrc
alias j='janito'
alias jg='janito -p google'
alias jo='janito -p openai'
alias jd='janito --profile developer -r -w -x'
```

### Windows (PowerShell)
```powershell
# No seu perfil PowerShell
Set-Alias j janito
Set-Alias jg "janito -p google"
```

## 🎯 Fluxo de Trabalho Recomendado

1. **Início**: Use modo interativo para explorar
2. **Desenvolvimento**: Use perfil developer com permissões apropriadas
3. **Documentação**: Use perfil writer para conteúdo
4. **Análise**: Use perfil analyst para dados
5. **Automação**: Crie scripts com comandos específicos

## 🆘 Problemas Comuns

### "Comando não encontrado"
- Verifique se o Janito está no PATH
- Use `python -m janito` como alternativa

### "Permissão negada"
- Use `-r -w -x` para habilitar permissões necessárias
- Verifique permissões de arquivo/diretório

### "API key inválida"
- Verifique se usou `--set-api-key` com `-p PROVEDOR`
- Confirme se a chave está ativa no site do provedor

## 📚 Próximos Passos

- [Configuração Avançada](configuracao.md)
- [Ferramentas Detalhadas](ferramentas.md)
- [Exemplos Práticos](exemplos.md)