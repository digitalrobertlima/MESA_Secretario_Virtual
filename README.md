```markdown
# 🏛️ M.E.S.A. | Secretário Virtual v4.5
> **Mentoria Estratégica Sistêmica Autônoma** > *Transformando a gestão acadêmica e profissional através da Inteligência Artificial.*

Este projeto é um Agente de Vendas e Assistente de Estudos desenvolvido para o **Prof. Robert Lima**. Ele automatiza o atendimento inicial, filtra leads interessados em aulas de AutoCAD/Revit e oferece suporte técnico em tempo real consultando a web.

---

## 📂 Estrutura do Projeto (Arquitetura Sistêmica)

```text
MESA_Secretario_Virtual/
├── .env                # Chaves secretas e tokens (NUNCA COMPARTILHAR)
├── .gitignore          # Filtro para o Git não subir arquivos sensíveis
├── main.py             # O "Cérebro" do bot (Motor Principal)
├── requirements.txt    # Lista de "peças" necessárias para o motor rodar
├── config/
│   └── settings.py     # Persona, Preços e Regras de Negócio
└── data/
    └── interessados.txt # Banco de dados simples de contatos gerados
```

---

## 🚀 Guia de Instalação (Do Zero ao Play)

Este guia foi feito para que qualquer pessoa, mesmo sem conhecimento em programação, consiga rodar o assistente.

### 1. Preparação dos Materiais
Antes de começar, você precisará de 3 chaves (tokens). Imagine que são as "senhas" para o bot ganhar vida:
1. **Telegram Token:** Criado via @BotFather no Telegram.
2. **Ollama API Key:** Obtida no site oficial da Ollama (ollama.com).
3. **Seu Chat ID:** Seu número de identificação no Telegram (para receber os avisos).

### 2. Configurando o Ambiente
Abra o seu terminal (CMD) e siga estes comandos:

```powershell
# Clone o repositório (ou baixe a pasta)
# Entre na pasta do projeto
cd MESA_Secretario_Virtual

# Crie um ambiente isolado para o bot (como uma bancada limpa de trabalho)
python -m venv .venv

# Ative essa bancada
.\.venv\Scripts\activate

# Instale todas as ferramentas necessárias automaticamente
pip install -r requirements.txt
```

### 3. O Arquivo Secreto (.env)
Crie um arquivo chamado `.env` na raiz do projeto e preencha assim:
```env
TELEGRAM_TOKEN=cole_seu_token_aqui
OLLAMA_API_KEY=cole_sua_chave_aqui
OLLAMA_MODEL=glm-4.7:cloud
MY_CHAT_ID=seu_id_aqui
```

### 4. Iniciando o Motor
Com tudo configurado, basta dar o comando de partida:
```powershell
python main.py
```

---

## 🧠 Funcionalidades de Alta Performance
- **Triagem Inteligente:** Diferencia dúvidas de estudos de intenções de compra.
- **Fechamento Estratégico:** Aplica gatilhos mentais e apresenta valores conforme o número de alunos.
- **Pesquisa em Tempo Real:** Se o aluno tiver uma dúvida técnica, o bot consulta a internet antes de responder.
- **Notificação Instantânea:** Emite um alerta sonoro no PC e avisa o Professor no celular assim que um novo lead fornece o WhatsApp.

---
**Design & Estratégia por Robert Lima** *Estética Industrial Organic Sophisticated com Luxo.*
```