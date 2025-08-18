# Perfis - Janito

Guia sobre como usar perfis para diferentes tipos de tarefas no Janito.

## 🎯 O que são Perfis?

Perfis são configurações pré-definidas que adaptam o comportamento do Janito para diferentes tipos de tarefas. Cada perfil tem:
- Prompt de sistema específico
- Ferramentas recomendadas
- Comportamento otimizado

## 📁 Perfis Disponíveis

### developer (Desenvolvedor)
**Uso:** Tarefas de programação e desenvolvimento
```bash
janito --profile developer
```

**Características:**
- Focado em código e debugging
- Sugere melhorias de código
- Ajuda com arquitetura
- Integração com ferramentas de desenvolvimento

**Exemplos de uso:**
```bash
# Refatoração de código
janito --profile developer -r -w -x "Refatore esta função Python"

# Debugging
janito --profile developer -r "Por que este código está lento?"

# Arquitetura
janito --profile developer "Projete uma API REST para e-commerce"
```

### writer (Escritor)
**Uso:** Criação de conteúdo e redação
```bash
janito --profile writer
```

**Características:**
- Focado em escrita clara e envolvente
- Ajuda com estrutura de texto
- Sugere melhorias gramaticais
- Adapta tom para público-alvo

**Exemplos de uso:**
```bash
# Blog post
janito --profile writer "Crie um post sobre IA para iniciantes"

# Email profissional
janito --profile writer "Redija um email de follow-up após entrevista"

# Documentação
janito --profile writer "Documente esta API REST"
```

### analyst (Analista)
**Uso:** Análise de dados e insights
```bash
janito --profile analyst
```

**Características:**
- Focado em análise quantitativa
- Identifica padrões e tendências
- Cria visualizações mentais
- Interpreta dados complexos

**Exemplos de uso:**
```bash
# Análise de CSV
janito --profile analyst -r "Analise este arquivo de vendas.csv"

# Insights de dados
janito --profile analyst "O que estes números dizem sobre nosso negócio?"

# Relatórios
janito --profile analyst "Crie um resumo executivo destes dados"
```

### teacher (Professor)
**Uso:** Ensino e aprendizado
```bash
janito --profile teacher
```

**Características:**
- Explica conceitos complexos de forma simples
- Usa analogias e exemplos
- Adapta nível de dificuldade
- Fomenta pensamento crítico

**Exemplos de uso:**
```bash
# Explicar conceito
janito --profile teacher "Explique recursão para iniciantes"

# Criar material didático
janito --profile teacher "Crie uma lição sobre loops em Python"

# Responder dúvidas
janito --profile teacher "Por que usamos funções?"
```

### debug (Debugging)
**Uso:** Solução de problemas técnicos
```bash
janito --profile debug
```

**Características:**
- Sistemático na identificação de problemas
- Sugere testes e verificações
- Analisa logs e erros
- Proporciona soluções passo a passo

**Exemplos de uso:**
```bash
# Debugging de código
janito --profile debug -r -x "Este script Python está crashando"

# Debugging de configuração
janito --profile debug "Por que minha API não responde?"

# Debugging de performance
janito --profile debug "Por que minha aplicação está lenta?"
```

## 🛠️ Como Criar Perfis Personalizados

### Método 1: Via Linha de Comando

```bash
# Criar perfil personalizado via variáveis
export JANITO_PROFILE_CUSTOM="Você é um especialista em..."
```

### Método 2: Via Arquivo de Configuração

Crie em `~/.janito/profiles/`:

```json
{
  "data-scientist": {
    "system_prompt": "Você é um cientista de dados experiente...",
    "preferred_tools": ["python", "pandas", "matplotlib"],
    "default_permissions": ["read", "execute"]
  }
}
```

### Método 3: Via Prompt de Sistema

```bash
# Usar prompt personalizado
janito -s meu_prompt.txt "sua tarefa"
```

## 🎭 Combinando Perfis com Permissões

### Desenvolvimento com Permissões Completas

```bash
# Perfil developer + todas as permissões
janito --profile developer -r -w -x
```

### Análise com Leitura de Arquivos

```bash
# Perfil analyst + leitura de dados
janito --profile analyst -r
```

### Escrita com Segurança

```bash
# Perfil writer + leitura/escrita (sem execução)
janito --profile writer -r -w
```

## 📊 Tabela de Perfis vs Casos de Uso

| Perfil | Melhor Para | Permissões Recomendadas | Exemplo |
|--------|-------------|------------------------|---------|
| developer | Código, debugging | -r -w -x | "Crie uma API REST" |
| writer | Conteúdo, documentação | -r -w | "Redija um blog post" |
| analyst | Dados, relatórios | -r | "Analise este CSV" |
| teacher | Ensino, explicações | (padrão) | "Explique conceitos" |
| debug | Problemas técnicos | -r -x | "Debug este erro" |

## 🎯 Fluxos de Trabalho por Perfil

### Workflow Developer

```bash
# 1. Iniciar com perfil developer
janito --profile developer -r -w -x

# 2. Dentro do chat:
"Crie estrutura para projeto Python"
"Implemente testes unitários"
"Configure CI/CD"
"Documente a API"
```

### Workflow Writer

```bash
# 1. Iniciar com perfil writer
janito --profile writer -r -w

# 2. Dentro do chat:
"Crie outline para artigo"
"Escreva introdução"
"Revise e melhore"
"Crie título chamativo"
```

### Workflow Analyst

```bash
# 1. Iniciar com perfil analyst
janito --profile analyst -r

# 2. Dentro do chat:
"Carregue e explore os dados"
"Crie visualizações"
"Identifique insights"
"Crie apresentação"
```

## 🔧 Dicas de Uso Avançado

### Alternando Perfis Dinamicamente

```bash
# No modo interativo, use:
# /role para mudar comportamento
# Exemplo: /role Você agora é um especialista em segurança
```

### Criando Scripts com Perfis

```bash
#!/bin/bash
# dev-helper.sh
janito --profile developer -r -w -x "$1"

# Uso
./dev-helper.sh "Refatore este código"
```

### Perfis por Projeto

```bash
# Criar aliases por projeto
echo 'alias proj-dev="janito --profile developer -r -w -x"' >> ~/.bashrc
echo 'alias proj-docs="janito --profile writer -r -w"' >> ~/.bashrc
```

## 🎨 Personalizando Perfis

### Prompt de Sistema Personalizado

```bash
# Criar perfil personalizado via prompt
janito -s custom_prompt.txt "sua tarefa"
```

Exemplo de `custom_prompt.txt`:
```
Você é um especialista em [SUA ÁREA].
Sempre [COMPORTAMENTO ESPECÍFICO].
Use [FORMATO PREFERIDO].
Considere [RESTRICOES/REGRAS].
```

### Perfis por Equipe

```bash
# Criar perfis para diferentes equipes
# Frontend team
janito --profile frontend-dev -r -w -x

# Backend team  
janito --profile backend-dev -r -w -x

# DevOps team
janito --profile devops -r -w -x
```

## 📈 Melhorando Produtividade com Perfis

### 1. Criar Atalhos por Perfil

```bash
# ~/.bashrc ou ~/.zshrc
alias jdev='janito --profile developer -r -w -x'
alias jwrite='janito --profile writer -r -w'
alias jdata='janito --profile analyst -r'
```

### 2. Scripts por Contexto

```bash
# code-review.sh
janito --profile developer -r "Faça code review de: $1"

# content-creation.sh  
janito --profile writer "Crie conteúdo sobre: $1"
```

### 3. Integração com IDEs

```bash
# Configurar no VS Code tasks
{
  "label": "Janito Developer",
  "type": "shell",
  "command": "janito --profile developer -r -w -x"
}
```

## 🆘 Solução de Problemas

### Perfil não encontrado

```bash
# Verificar perfis disponíveis
# Perfis são baseados em templates em agent/templates/
# Ou use prompts personalizados
```

### Comportamento inesperado

```bash
# Resetar para padrão
janito --set provider=google
janito --set google.model=gemini-2.5-flash

# Ou reiniciar conversa
# No chat: /restart
```

## 📚 Próximos Passos

1. **Experimente cada perfil** com tarefas reais
2. **Crie seus próprios prompts** personalizados
3. **Combine perfis** com permissões específicas
4. **Crie scripts** automatizados por perfil
5. **Compartilhe** configurações com sua equipe

---

**Dica:** Comece com o perfil que mais se alinha com sua tarefa principal e ajuste conforme necessário!