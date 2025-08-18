# Ferramentas - Janito

Guia completo sobre as ferramentas disponíveis no Janito e como usá-las.

## 🔧 Visão Geral das Ferramentas

Janito oferece três categorias de ferramentas:
- **📖 Leitura** (`-r`): Ler arquivos, buscar informações
- **✏️ Escrita** (`-w`): Criar, editar, modificar arquivos
- **⚡ Execução** (`-x`): Executar código, comandos, scripts

## 🛡️ Segurança e Permissões

### Por que as ferramentas estão desabilitadas?
Por segurança, todas as ferramentas começam desabilitadas. Você deve habilitar explicitamente.

### Como habilitar ferramentas?

```bash
# Habilitar leitura apenas
janito -r "Leia este arquivo"

# Habilitar leitura e escrita
janito -r -w "Edite este arquivo"

# Habilitar todas as ferramentas
janito -r -w -x "Execute este código"

# No modo interativo
janito
# /read on
# /write on
# /execute on
```

## 📖 Ferramentas de Leitura

### 1. Leitura de Arquivos

```bash
# Ler arquivo específico
janito -r "Leia o arquivo README.md"

# Ler múltiplos arquivos
janito -r "Compare arquivo1.py e arquivo2.py"

# Ler diretório inteiro
janito -r "Analise a estrutura da pasta src/"
```

### 2. Busca de Texto

```bash
# Buscar em arquivos
janito -r "Busque todas as funções Python em *.py"

# Buscar padrões específicos
janito -r "Encontre todos os TODOs no código"

# Buscar com regex
janito -r "Busque emails no formato exemplo@dominio.com"
```

### 3. Análise de Código

```bash
# Análise de código Python
janito -r "Analise este arquivo Python para problemas"

# Análise de dependências
janito -r "Liste todas as dependências deste projeto"

# Análise de complexidade
janito -r "Calcule a complexidade deste código"
```

## ✏️ Ferramentas de Escrita

### 1. Criação de Arquivos

```bash
# Criar novo arquivo
janito -w "Crie um arquivo requirements.txt com Flask"

# Criar múltiplos arquivos
janito -w "Crie estrutura MVC para projeto Python"

# Criar documentação
janito -w "Documente esta API REST no formato OpenAPI"
```

### 2. Edição de Arquivos

```bash
# Adicionar conteúdo
janito -r -w "Adicione docstrings a este arquivo Python"

# Refatorar código
janito -r -w "Refatore esta função para ser mais eficiente"

# Atualizar configurações
janito -r -w "Atualize as versões no requirements.txt"
```

### 3. Renomear e Organizar

```bash
# Renomear arquivos
janito -w "Renomeie test.py para test_main.py"

# Reorganizar estrutura
janito -r -w "Reorganize esta pasta por funcionalidade"

# Limpar código
janito -r -w "Remova código não utilizado"
```

## ⚡ Ferramentas de Execução

### 1. Execução de Python

```bash
# Executar código Python
janito -x "Execute: print('Hello, World!')"

# Testar funções
janito -r -x "Teste esta função Python"

# Instalar pacotes
janito -x "Execute: pip install requests"
```

### 2. Comandos do Sistema

```bash
# Comandos Linux/Mac
janito -x "Execute: ls -la"
janito -x "Execute: git status"
janito -x "Execute: docker ps"

# Comandos Windows
janito -x "Execute: dir"
janito -x "Execute: ipconfig"
```

### 3. Scripts e Automação

```bash
# Executar scripts
janito -x "Execute o script: python setup.py"

# Testes automatizados
janito -x "Execute: python -m pytest"

# Build e deploy
janito -x "Execute: npm run build"
```

## 🎯 Exemplos Práticos por Categoria

### Desenvolvimento Web

```bash
# Analisar projeto existente
janito -r "Analise esta aplicação Flask"

# Criar nova estrutura
janito -w "Crie estrutura para API REST com Flask"

# Executar e testar
janito -r -x "Configure e teste esta API"
```

### Análise de Dados

```bash
# Ler dados
janito -r "Carregue e explore este arquivo CSV"

# Processar dados
janito -r -w "Limpe e processe estes dados"

# Visualizar
janito -r -x "Crie visualizações com matplotlib"
```

### DevOps

```bash
# Analisar infraestrutura
janito -r "Analise este Dockerfile"

# Criar configurações
janito -w "Crie docker-compose.yml para este projeto"

# Deploy
janito -x "Execute: docker-compose up -d"
```

## 🔍 Ferramentas de Busca Avançada

### 1. Busca Recursiva

```bash
# Buscar em subdiretórios
janito -r "Busque todos os arquivos .py com funções async"

# Buscar por tipo
janito -r "Liste todos os arquivos de configuração"

# Buscar por data
janito -r "Encontre arquivos modificados hoje"
```

### 2. Análise de Conteúdo

```bash
# Contar linhas de código
janito -r "Conte linhas de código em cada arquivo .py"

# Análise de imports
janito -r "Liste todas as bibliotecas usadas"

# Duplicação de código
janito -r "Identifique código duplicado"
```

## 🛠️ Ferramentas de Refatoração

### 1. Renomeação Inteligente

```bash
# Renomear variáveis
janito -r -w "Renomeie variáveis para serem mais descritivas"

# Renomear funções
janito -r -w "Renomeie funções seguindo convenções Python"

# Renomear arquivos
janito -r -w "Renomeie arquivos para padrão snake_case"
```

### 2. Extração e Organização

```bash
# Extrair funções
janito -r -w "Extraia esta lógica para uma função separada"

# Criar módulos
janito -r -w "Organize este código em módulos"

# Criar classes
janito -r -w "Converta esta estrutura para classes"
```

## 📊 Ferramentas de Documentação

### 1. Geração Automática

```bash
# Gerar README
janito -r -w "Crie README.md para este projeto"

# Gerar docstrings
janito -r -w "Adicione docstrings a todas as funções"

# Gerar changelog
janito -r -w "Crie CHANGELOG.md baseado nos commits"
```

### 2. Diagramas e Visualização

```bash
# Criar diagramas
janito -w "Crie diagrama de arquitetura deste sistema"

# Documentar fluxo
janito -r -w "Documente o fluxo de dados desta aplicação"

# Criar tutoriais
janito -w "Crie tutorial de instalação passo a passo"
```

## 🔄 Ferramentas de Versionamento

### 1. Git Integration

```bash
# Verificar status
janito -x "Execute: git status"

# Criar commits
janito -r -x "Crie commit message para estas mudanças"

# Gerenciar branches
janito -x "Execute: git branch -a"
```

### 2. Versionamento Semântico

```bash
# Atualizar versão
janito -r -w "Atualize versão no setup.py para 1.2.0"

# Criar tags
janito -x "Execute: git tag v1.2.0"

# Criar release
janito -w "Crie notas de release para v1.2.0"
```

## 🧪 Ferramentas de Teste

### 1. Testes Unitários

```bash
# Criar testes
janito -r -w "Crie testes unitários para esta função"

# Executar testes
janito -x "Execute: python -m pytest"

# Analisar cobertura
janito -x "Execute: coverage run -m pytest"
```

### 2. Testes de Integração

```bash
# Criar testes de API
janito -r -w "Crie testes de integração para esta API"

# Testar endpoints
janito -x "Execute: curl http://localhost:5000/api/test"

# Verificar respostas
janito -r -x "Teste todos os endpoints da API"
```

## 🚀 Ferramentas de Deploy

### 1. Containerização

```bash
# Criar Dockerfile
janito -w "Crie Dockerfile otimizado para esta aplicação"

# Criar docker-compose
janito -w "Crie docker-compose.yml com banco de dados"

# Build e deploy
janito -x "Execute: docker build -t minha-app ."
```

### 2. Deploy em Nuvem

```bash
# Configurar AWS
janito -w "Crie configuração para deploy AWS"

# Configurar Heroku
janito -w "Crie Procfile para Heroku"

# Deploy script
janito -w "Crie script de deploy automatizado"
```

## 🎯 Dicas de Segurança

### 1. Verificar antes de Executar

```bash
# Sempre revisar antes de executar
janito -r -w "Mostre o que será executado antes de rodar"

# Executar em sandbox
janito -x "Execute em ambiente isolado"
```

### 2. Backup Antes de Mudanças

```bash
# Criar backup
janito -x "Execute: cp -r projeto projeto_backup"

# Usar git para tracking
janito -x "Execute: git add . && git commit -m 'Backup antes de mudanças'"
```

## 📋 Checklist de Ferramentas

### Antes de Começar
- [ ] Entender as permissões necessárias
- [ ] Fazer backup de arquivos importantes
- [ ] Testar em ambiente seguro

### Durante Uso
- [ ] Revisar comandos antes de executar
- [ ] Verificar logs de execução
- [ ] Testar mudanças incrementalmente

### Após Uso
- [ ] Verificar se tudo funcionou
- [ ] Commitar mudanças no git
- [ ] Documentar o que foi feito

## 🆘 Solução de Problemas

### Ferramenta não funciona

```bash
# Verificar permissões
janito --list-tools

# Testar permissão específica
janito -r "teste simples"
```

### Arquivo não encontrado

```bash
# Verificar caminho
janito -r "Liste arquivos no diretório atual"

# Usar caminho absoluto
janito -r "Leia /caminho/completo/arquivo.txt"
```

### Permissão negada

```bash
# Linux/Mac: usar sudo se necessário
# Windows: executar como administrador
# Verificar permissões do arquivo
```

## 📚 Próximos Passos

1. **Experimente** cada categoria de ferramenta
2. **Combine** ferramentas para tarefas complexas
3. **Crie scripts** automatizados
4. **Documente** seus workflows favoritos
5. **Compartilhe** com a comunidade

---

**Lembre-se:** Sempre use ferramentas com cuidado e faça backups antes de operações importantes!