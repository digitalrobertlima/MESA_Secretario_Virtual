import os
import winsound
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from ollama import AsyncClient
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from rich.console import Console
from rich.panel import Panel
from duckduckgo_search import DDGS

# --- AMBIENTE E CONFIGURAÇÕES ---
console = Console()
base_path = Path(__file__).resolve().parent
load_dotenv(dotenv_path=base_path / '.env', override=True)

try:
    from config.settings import SYSTEM_PROMPT, THEME_COLOR
except ImportError:
    console.print("[bold red]❌ Erro:[/bold red] Verifique se 'THEME_COLOR' existe no seu settings.py")
    exit()

# Variáveis do .env
API_KEY = os.getenv("OLLAMA_API_KEY")
TOKEN_TEL = os.getenv("TELEGRAM_TOKEN")
MODELO_CLOUD = os.getenv("OLLAMA_MODEL")
MY_CHAT_ID = os.getenv("MY_CHAT_ID")
LIMITE_MEMORIA = 10 
memorias = {}

# Cliente Cloud Único
cloud_client = AsyncClient(
    host='https://api.ollama.com',
    headers={'Authorization': f'Bearer {API_KEY}'}
)

# --- FUNÇÕES SUPORTE ---

def alerta_sonoro():
    """Bip duplo de notificação no Windows"""
    winsound.Beep(1000, 150)
    winsound.Beep(1400, 200)

def pesquisar_na_web(termo):
    """Realiza busca técnica no DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            resultados = [r for r in ddgs.text(termo, max_results=3)]
            contexto = "\n".join([f"Fonte: {r['title']} - {r['body']}" for r in resultados])
            return contexto if contexto else "Nenhum resultado relevante encontrado."
    except Exception as e:
        return f"Erro na pesquisa web: {e}"

async def notificar_robert(context, resumo):
    """Envia o lead para o seu Telegram pessoal"""
    if MY_CHAT_ID:
        try:
            await context.bot.send_message(
                chat_id=MY_CHAT_ID, 
                text=f"🚨 **NOVO CONTATO M.E.S.A.**\n\n{resumo}",
                parse_mode='Markdown'
            )
        except Exception as e:
            console.print(f"[red]Erro na notificação pessoal: {e}[/red]")

# --- NÚCLEO DO AGENTE ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    memorias[user_id] = []
    alerta_sonoro()
    await update.message.reply_text("Olá! Sou o assistente do Prof. Robert Lima. Como posso ajudar com aulas ou dúvidas hoje?")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    user_name = update.effective_user.first_name
    
    if user_id not in memorias:
        memorias[user_id] = []
        alerta_sonoro()

    console.print(Panel(f"[b]{user_name}:[/b] {user_text}", border_style=THEME_COLOR))

    try:
        # GATILHOS DE BUSCA (Para dúvidas técnicas ou curiosidades)
        contexto_web = ""
        termos_pesquisa = ['como', 'o que', 'qual', 'erro', 'comando', 'norma', 'uemg', 'cefet', 'novidade', '?']
        
        if any(t in user_text.lower() for t in termos_pesquisa):
            console.print("[cyan]🌐 Pesquisando na Web para suporte técnico...[/cyan]")
            dados_web = pesquisar_na_web(user_text)
            contexto_web = f"\n\n[DADOS RECENTES DA WEB]:\n{dados_web}\n(Use esses dados para responder. Você TEM acesso à internet através deste contexto!)"

        # CHAMADA AO GLM-4.7 CLOUD
        console.print(f"[green]🚀 GLM-4.7 Cloud processando...[/green]")
        
        # Instrução extra para evitar a 'teimosia' da IA sobre não ter internet
        instrucao_fix = "\nNota: Se houver dados da web acima, utilize-os. Não diga que não pode pesquisar."
        
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT + contexto_web + instrucao_fix}]
        messages += memorias[user_id]
        messages += [{'role': 'user', 'content': user_text}]

        response = await cloud_client.chat(model=MODELO_CLOUD, messages=messages)
        reply = response['message']['content']

        # Atualiza Memória
        memorias[user_id].append({'role': 'user', 'content': user_text})
        memorias[user_id].append({'role': 'assistant', 'content': reply})
        memorias[user_id] = memorias[user_id][-LIMITE_MEMORIA:]

        # FECHAMENTO DE LEAD (Se tiver número de telefone)
        if any(char.isdigit() for char in user_text) and len(user_text) >= 8:
            with open('data/interessados.txt', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now()} | {user_name} | {user_text}\n")
            
            await notificar_robert(context, f"O usuário **{user_name}** enviou um contato!\n\n*Mensagem:* {user_text}")
            console.print("[bold gold1]💾 Lead registrado com sucesso![/bold gold1]")

        await update.message.reply_text(reply)
        console.print("[bold green]✔ Ciclo finalizado.[/bold green]")

    except Exception as e:
        console.print(f"[bold red]❌ ERRO:[/bold red] {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TEL).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))
    
    console.print(Panel("🤖 AGENTE M.E.S.A. v4.5 ONLINE (FULL CLOUD)", style="bold green"))
    app.run_polling()