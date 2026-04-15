import os
import winsound
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from ollama import AsyncClient
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from rich.console import Console
from rich.panel import Panel

# 1. Configuração de Ambiente e Caminhos
console = Console()
base_path = Path(__file__).resolve().parent
load_dotenv(dotenv_path=base_path / '.env', override=True)

# 2. Importação Segura das suas Configurações
try:
    from config.settings import SYSTEM_PROMPT, THEME_COLOR
except ImportError as e:
    console.print(f"[bold red]❌ ERRO DE IMPORTAÇÃO:[/bold red] {e}")
    console.print("[yellow]Certifique-se de que o arquivo config/settings.py possui THEME_COLOR definido.[/yellow]")
    exit()

# 3. Variáveis Globais
MY_CHAT_ID = os.getenv("MY_CHAT_ID")
API_KEY = os.getenv("OLLAMA_API_KEY")
TOKEN_TEL = os.getenv("TELEGRAM_TOKEN")
MODELO_CLOUD = os.getenv("OLLAMA_MODEL")
LIMITE_MEMORIA = 10 
memorias = {}

# 4. Inicialização dos Clientes Ollama
local_client = AsyncClient() 
cloud_client = AsyncClient(
    host='https://api.ollama.com',
    headers={'Authorization': f'Bearer {API_KEY}'}
)

# --- FUNÇÕES DE APOIO ---

def alerta_sonoro():
    """Bip duplo para avisar que tem cliente na linha"""
    winsound.Beep(800, 150)
    winsound.Beep(1200, 200)

async def notificar_robert(context, resumo):
    """Envia o lead direto para o seu Telegram pessoal"""
    if MY_CHAT_ID:
        try:
            await context.bot.send_message(
                chat_id=MY_CHAT_ID, 
                text=f"🚨 **NOVO CONTATO M.E.S.A.**\n\n{resumo}",
                parse_mode='Markdown'
            )
        except Exception as e:
            console.print(f"[red]Erro ao te notificar: {e}[/red]")

# --- HANDLERS DO TELEGRAM ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    memorias[user_id] = [] # Limpa memória ao dar start
    alerta_sonoro()
    
    boas_vindas = (
        "Olá! Sou o assistente executivo do Prof. Robert Lima. "
        "Como posso ajudar você com aulas de AutoCAD, Revit ou projetos de design hoje?"
    )
    await update.message.reply_text(boas_vindas)
    console.print(f"[green]🆕 {update.effective_user.first_name} iniciou o bot.[/green]")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    user_name = update.effective_user.first_name

    # Inicializa memória
    if user_id not in memorias:
        memorias[user_id] = []
        alerta_sonoro()

    console.print(Panel(f"[b]{user_name}:[/b] {user_text}", border_style=THEME_COLOR))

    try:
        # FASE 1: TRIAGEM LOCAL (Llama 3.2 1B)
        console.print("[yellow]🔍 Triagem...[/yellow]")
        prompt_filtro = (
            "Responda apenas 'AGIR' se a mensagem for sobre aulas, software, preços, "
            "ou se for uma resposta a uma pergunta sua. "
            "Responda 'SAUDAR' se for apenas um oi ou algo irrelevante.\n"
            f"Mensagem: {user_text}\nResposta:"
        )
        check = await local_client.chat(model='llama3.2:1b', messages=[{'role': 'user', 'content': prompt_filtro}])
        decisao = check['message']['content'].strip().upper()
        
        # Rede de Segurança (Keywords)
        gatilhos = ['aula', 'valor', 'preço', 'horário', 'cad', 'revit', '319', 'uemg', 'biblioteca']
        forcar_agir = any(word in user_text.lower() for word in gatilhos)

        # FASE 2: RESPOSTA (LOCAL OU CLOUD)
        if "AGIR" in decisao or forcar_agir:
            console.print("[green]🚀 Acionando GLM-4.7 Cloud...[/green]")
            
            # Monta histórico para a nuvem
            messages = [{'role': 'system', 'content': SYSTEM_PROMPT}] + memorias[user_id] + [{'role': 'user', 'content': user_text}]
            
            response = await cloud_client.chat(model=MODELO_CLOUD, messages=messages)
            reply = response['message']['content']

            # Atualiza Memória
            memorias[user_id].append({'role': 'user', 'content': user_text})
            memorias[user_id].append({'role': 'assistant', 'content': reply})
            memorias[user_id] = memorias[user_id][-LIMITE_MEMORIA:]

            # Verificação de Fechamento (Se tem número de telefone)
            if any(char.isdigit() for char in user_text) and len(user_text) >= 8:
                # Salva no arquivo
                with open('data/interessados.txt', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.now()} | {user_name} | {user_text}\n")
                
                # Te avisa no seu chat privado
                await notificar_robert(context, f"O usuário **{user_name}** enviou um contato!\n\n*Mensagem:* {user_text}")
                console.print("[bold gold1]💾 Lead salvo e Robert notificado![/bold gold1]")
        else:
            reply = "Olá! Como o Prof. Robert Lima pode te ajudar hoje?"

        await update.message.reply_text(reply)
        console.print("[bold green]✔ Ciclo finalizado.[/bold green]")

    except Exception as e:
        console.print(f"[bold red]❌ ERRO:[/bold red] {e}")

if __name__ == '__main__':
    if not TOKEN_TEL or not API_KEY:
        console.print("[red]Faltam credenciais no .env![/red]")
    else:
        app = ApplicationBuilder().token(TOKEN_TEL).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))
        
        console.print(Panel("🤖 AGENTE M.E.S.A. v2.1 ONLINE", style="bold green"))
        app.run_polling()