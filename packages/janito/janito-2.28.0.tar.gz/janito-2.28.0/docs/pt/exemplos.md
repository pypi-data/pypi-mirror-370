# Exemplos Práticos - Janito

Coleção de exemplos práticos para usar o Janito em situações reais.

## 🚀 Exemplos para Iniciantes

### Exemplo 1: Primeira Conversa

```bash
# Iniciar modo interativo
janito -p google

# Dentro do chat:
"Olá! Me explique o que é inteligência artificial de forma simples"
```

### Exemplo 2: Análise Simples

```bash
# Analisar um arquivo de texto
janito -r "Leia o arquivo README.md e me diga do que se trata"
```

### Exemplo 3: Criar Conteúdo

```bash
# Criar um arquivo simples
janito -w "Crie um arquivo ola_mundo.py com um print('Olá, Mundo!')"
```

## 💻 Desenvolvimento Web

### Criar API REST com Flask

```bash
# 1. Criar estrutura do projeto
janito --profile developer -w "Crie estrutura básica para API REST Flask"

# 2. Criar modelo de dados
janito --profile developer -w "Crie modelo User com SQLAlchemy"

# 3. Criar endpoints
janito --profile developer -w "Crie endpoints CRUD para usuários"

# 4. Testar API
janito --profile developer -x "Execute: python app.py"
```

### Debug de Aplicação Web

```bash
# Analisar erro
janito --profile debug -r -x "Debug este erro 500 no Flask"

# Verificar logs
janito --profile debug -r "Analise os logs de erro"

# Propor solução
janito --profile debug "Como resolver problema de CORS?"
```

### Dockerização

```bash
# Criar Dockerfile
janito --profile developer -w "Crie Dockerfile para Flask API"

# Criar docker-compose
janito --profile developer -w "Crie docker-compose.yml com PostgreSQL"

# Build e teste
janito --profile developer -x "Execute: docker-compose up --build"
```

## 📊 Análise de Dados

### Explorar CSV

```bash
# 1. Carregar e explorar dados
janito --profile analyst -r "Carregue e explore vendas_2024.csv"

# 2. Limpar dados
janito --profile analyst -r -w "Limpe dados nulos e duplicados"

# 3. Análise exploratória
janito --profile analyst -r -x "Crie análise exploratória dos dados"

# 4. Visualizações
janito --profile analyst -r -x "Crie gráficos de vendas por mês"
```

### Criar Dashboard

```bash
# Criar script de dashboard
janito --profile analyst -w "Crie dashboard interativo com Plotly"

# Executar dashboard
janito --profile analyst -x "Execute: python dashboard.py"
```

### Machine Learning Básico

```bash
# Preparar dados
janito --profile analyst -r -w "Prepare dados para modelo ML"

# Criar modelo
janito --profile analyst -w "Crie modelo de previsão de vendas"

# Avaliar modelo
janito --profile analyst -x "Execute treinamento e avaliação"
```

## 📝 Automação de Documentação

### Gerar README

```bash
# Analisar projeto
janito --profile writer -r "Analise toda a estrutura do projeto"

# Criar README
janito --profile writer -w "Crie README.md completo com:
- Descrição
- Instalação
- Uso
- Exemplos
- Contribuição"
```

### Documentar Código

```bash
# Adicionar docstrings
janito --profile writer -r -w "Adicione docstrings a todas as funções"

# Criar documentação API
janito --profile writer -w "Crie documentação OpenAPI/Swagger"

# Gerar changelog
janito --profile writer -w "Crie CHANGELOG.md baseado nos commits"
```

### Criar Tutoriais

```bash
# Tutorial de instalação
janito --profile writer -w "Crie tutorial passo a passo de instalação"

# Tutorial de uso
janito --profile writer -w "Crie tutorial com exemplos práticos"
```

## 🧪 Testes e Qualidade

### Configurar Pytest

```bash
# Criar estrutura de testes
janito --profile developer -w "Configure pytest para este projeto"

# Criar testes unitários
janito --profile developer -r -w "Crie testes para funções principais"

# Executar testes
janito --profile developer -x "Execute: python -m pytest -v"
```

### Configurar CI/CD

```bash
# Criar GitHub Actions
janito --profile developer -w "Crie workflow GitHub Actions para testes"

# Criar configuração de lint
janito --profile developer -w "Configure pre-commit hooks"

# Configurar deploy automático
janito --profile developer -w "Crie deploy automático para Heroku"
```

### Análise de Qualidade

```bash
# Executar lint
janito --profile developer -x "Execute: flake8 ."

# Análise de complexidade
janito --profile developer -x "Execute: radon cc -s ."

# Relatório de qualidade
janito --profile developer -w "Crie relatório de qualidade do código"
```

## 🔧 DevOps e Infraestrutura

### Configurar Nginx

```bash
# Criar configuração Nginx
janito --profile devops -w "Crie configuração Nginx para Flask"

# Testar configuração
janito --profile devops -x "Teste configuração Nginx"
```

### Configurar SSL

```bash
# Criar configuração SSL
janito --profile devops -w "Configure SSL com Let's Encrypt"

# Renovar certificados
janito --profile devops -x "Configure renovação automática SSL"
```

### Monitoramento

```bash
# Criar sistema de logs
janito --profile devops -w "Configure sistema de logging"

# Criar monitoramento
janito --profile devops -w "Configure health checks"
```

## 🎨 Frontend e Design

### Criar Interface Web

```bash
# Criar HTML/CSS básico
janito --profile developer -w "Crie página HTML responsiva com CSS"

# Adicionar JavaScript
janito --profile developer -w "Adicione interatividade com JavaScript"

# Testar interface
janito --profile developer -x "Execute servidor local para testar"
```

### React/Vue Components

```bash
# Criar componente React
janito --profile developer -w "Crie componente React para formulário"

# Criar componente Vue
janito --profile developer -w "Crie componente Vue para lista de items"
```

## 📱 Mobile Development

### Criar API para App

```bash
# Criar API para mobile
janito --profile developer -w "Crie API REST para app mobile"

# Adicionar autenticação
janito --profile developer -w "Adicione autenticação JWT"

# Documentar API
janito --profile developer -w "Documente API para desenvolvedores mobile"
```

## 🗄️ Banco de Dados

### Configurar PostgreSQL

```bash
# Criar schema
janito --profile developer -w "Crie schema PostgreSQL para e-commerce"

# Criar migrations
janito --profile developer -w "Crie migrations para tabelas"

# Popular dados
janito --profile developer -w "Crie script para popular banco com dados de teste"
```

### MongoDB

```bash
# Criar schema MongoDB
janito --profile developer -w "Modele dados para MongoDB"

# Criar queries
janito --profile developer -w "Crie queries otimizadas para MongoDB"
```

## 🤖 Automação de Tarefas

### Script Diário

```bash
#!/bin/bash
# backup-diario.sh

# Criar script com Janito
janito --profile developer -w "Crie script de backup diário para PostgreSQL"

# Agendar com cron
janito --profile developer -w "Configure cron para backup automático"
```

### Processamento de Imagens

```bash
# Criar script de processamento
janito --profile developer -w "Crie script para redimensionar imagens em lote"

# Executar processamento
janito --profile developer -x "Execute processamento de imagens"
```

### Web Scraping

```bash
# Criar scraper
janito --profile developer -w "Crie web scraper para extrair dados"

# Executar scraper
janito --profile developer -x "Execute scraper e salve dados em CSV"
```

## 📊 Relatórios e Dashboards

### Criar Relatório de Vendas

```bash
# 1. Analisar dados
janito --profile analyst -r "Analise vendas_2024.csv"

# 2. Criar visualizações
janito --profile analyst -w "Crie gráficos de vendas por região"

# 3. Gerar relatório PDF
janito --profile analyst -w "Crie relatório PDF executivo"
```

### Dashboard em Tempo Real

```bash
# Criar dashboard
janito --profile developer -w "Crie dashboard em tempo real com Streamlit"

# Deploy dashboard
janito --profile developer -x "Execute dashboard na porta 8501"
```

## 🎯 Workflows Completos

### Workflow: Novo Projeto Python

```bash
# 1. Criar estrutura
janito --profile developer -w "Crie estrutura completa para projeto Python"

# 2. Configurar ambiente
janito --profile developer -w "Configure virtual environment e requirements"

# 3. Criar testes
janito --profile developer -w "Configure pytest e crie testes iniciais"

# 4. Documentar
janito --profile writer -w "Crie documentação completa do projeto"

# 5. Configurar CI/CD
janito --profile developer -w "Configure GitHub Actions para testes automáticos"
```

### Workflow: Análise de Dados

```bash
# 1. Explorar dados
janito --profile analyst -r "Explore dataset de e-commerce"

# 2. Limpar dados
janito --profile analyst -r -w "Limpe e prepare dados"

# 3. Análise
janito --profile analyst -x "Execute análise exploratória completa"

# 4. Modelagem
janito --profile analyst -w "Crie modelo de previsão de churn"

# 5. Relatório
janito --profile writer -w "Crie relatório executivo dos resultados"
```

### Workflow: Deploy de Aplicação

```bash
# 1. Preparar aplicação
janito --profile developer -r "Prepare aplicação para produção"

# 2. Containerizar
janito --profile devops -w "Crie Dockerfile e docker-compose"

# 3. Configurar servidor
janito --profile devops -w "Configure Nginx e SSL"

# 4. Deploy
janito --profile devops -x "Execute deploy para produção"

# 5. Monitorar
janito --profile devops -w "Configure monitoramento e alertas"
```

## 🆘 Exemplos de Debugging

### Debug Python

```bash
# Analisar erro
janito --profile debug -r -x "Debug este erro: ImportError: No module named 'xyz'"

# Memory leak
janito --profile debug -r -x "Identifique memory leak neste código"

# Performance
janito --profile debug -r -x "Otimize este código lento"
```

### Debug Infraestrutura

```bash
# Docker issues
janito --profile debug -x "Debug erro de container não iniciando"

# Database issues
janito --profile debug -x "Debug erro de conexão PostgreSQL"

# Network issues
janito --profile debug -x "Debug problema de rede na aplicação"
```

## 📚 Templates Úteis

### Template de Script Python

```bash
# Criar script template
janito --profile developer -w "Crie template de script Python com argparse, logging e estrutura modular"
```

### Template de API

```bash
# Criar API template
janito --profile developer -w "Crie template de API REST com Flask, autenticação e documentação"
```

### Template de Análise

```bash
# Criar notebook template
janito --profile analyst -w "Crie template de notebook Jupyter para análise de dados"
```

## 🎯 Quick Start por Área

### Data Science

```bash
# 5 minutos para análise de dados
janito --profile analyst -r -x "Crie análise rápida de dados de vendas"
```

### Web Development

```bash
# 5 minutos para API REST
janito --profile developer -w -x "Crie API REST básica em 5 minutos"
```

### DevOps

```bash
# 5 minutos para deploy
janito --profile devops -w -x "Crie deploy automático em 5 minutos"
```

---

**💡 Dica:** Comece com exemplos simples e vá aumentando a complexidade gradualmente. Use os perfis apropriados para cada tarefa!