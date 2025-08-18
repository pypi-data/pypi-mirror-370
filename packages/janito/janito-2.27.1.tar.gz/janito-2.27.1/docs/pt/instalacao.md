# Instalação - Janito

Este guia irá ajudá-lo a instalar o Janito em seu sistema.

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git (para instalação a partir do repositório)

## 🚀 Instalação

### Método 1: Instalação via pip (Recomendado)

```bash
pip install git+https://github.com/ikignosis/janito.git
```

### Método 2: Instalação em modo desenvolvedor

Se você quiser contribuir para o projeto ou precisar da versão mais recente:

```bash
git clone https://github.com/ikignosis/janito.git
cd janito
pip install -e .
```

### Método 3: Instalação via pip + GitHub (SSH)

```bash
pip install git+ssh://git@github.com/ikignosis/janito.git
```

## ✅ Verificando a Instalação

Após a instalação, verifique se o Janito foi instalado corretamente:

```bash
janito --version
```

Você deve ver algo como:
```
janito version X.Y.Z
```

## 🛠️ Configuração Inicial

### 1. Obter Chave de API

Antes de usar o Janito, você precisará de uma chave de API de um provedor LLM suportado:

- **Google Gemini** (Gratuito com limitações): [Obter chave aqui](https://aistudio.google.com/app/apikey)
- **OpenAI**: [Obter chave aqui](https://platform.openai.com/api-keys)
- **Anthropic**: [Obter chave aqui](https://console.anthropic.com/)
- **DeepSeek**: [Obter chave aqui](https://platform.deepseek.com/)

### 2. Configurar sua Primeira Chave

```bash
# Para Google Gemini (recomendado para iniciantes)
janito --set-api-key SUA_CHAVE_AQUI -p google

# Para OpenAI
janito --set-api-key sk-sua-chave-aqui -p openai

# Para Anthropic
janito --set-api-key sk-ant-sua-chave-aqui -p anthropic
```

### 3. Testar a Instalação

```bash
# Teste básico
janito -p google "Olá, qual é a capital do Brasil?"

# Verificar provedores disponíveis
janito --list-providers

# Verificar modelos disponíveis
janito -p google --list-models
```

## 🐛 Solução de Problemas

### Problema: "janito: command not found"

**Solução:**
```bash
# Verificar se está no PATH
python -m janito --version

# Ou usar o caminho completo
~/.local/bin/janito --version
```

### Problema: Erro de permissão no Windows

**Solução:**
Execute o terminal como administrador ou use:
```bash
pip install --user janito
```

### Problema: Conflito de versões Python

**Solução:**
```bash
# Usar Python 3 explicitamente
python3 -m pip install git+https://github.com/ikignosis/janito.git

# Ou usar pip3
pip3 install git+https://github.com/ikignosis/janito.git
```

### Problema: Erro SSL/TLS

**Solução:**
```bash
# Atualizar certificados
pip install --upgrade certifi

# Ou desabilitar verificação SSL (não recomendado)
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org git+https://github.com/ikignosis/janito.git
```

## 🔄 Atualização

Para atualizar o Janito para a versão mais recente:

```bash
pip install --upgrade git+https://github.com/ikignosis/janito.git
```

Se instalou em modo desenvolvedor:
```bash
cd janito
git pull
pip install -e .
```

## 📚 Próximos Passos

Após a instalação bem-sucedida:

1. [Guia de Uso](guia-uso.md) - Aprenda os comandos básicos
2. [Configuração](configuracao.md) - Configure provedores e modelos
3. [Perfis](perfis.md) - Use perfis para diferentes tarefas

## 🆘 Precisa de Ajuda?

- [FAQ](faq-pt.md) - Perguntas frequentes
- [Issues no GitHub](https://github.com/ikignosis/janito/issues)
- [Discussions](https://github.com/ikignosis/janito/discussions)