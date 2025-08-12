# Importa las clases necesarias de la librería python-telegram-bot
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests  # Para hacer peticiones HTTP al backend
import os

# Token del bot de Telegram (debería mantenerse privado en producción)
TOKEN = os.getenv("TELEGRAM_TOKEN", "7342077363:AAGuI9fAULbbcY4EFce8nRRkEmbUXy113rc")
# URL del backend FastAPI al que se enviarán los mensajes
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://0.0.0.0:8000/chat")

# Handler para el comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        # Responde con un mensaje de bienvenida y ejemplo de uso
        await update.message.reply_text("¡Hola! Mándame un mensaje con un ticket Jira, por ejemplo: estado SD-497")

# Handler para mensajes de texto que no son comandos
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return  # Si no hay mensaje, no hace nada
    
    texto = update.message.text  # Obtiene el texto enviado por el usuario

    try:
        # Enviar mensaje al backend FastAPI
        response = requests.post(
            FASTAPI_URL,
            json={"mensaje": texto},
            timeout=300  # Timeout de 5 minutos
        )
        if response.status_code == 200:
            data = response.json()
            respuesta = data.get("respuesta", "No hay respuesta")  # Obtiene la respuesta del backend
        else:
            respuesta = f"Error al conectar con el backend (código: {response.status_code})"  # Mensaje de error si falla la conexión
    except requests.exceptions.RequestException as e:
        respuesta = f"Error de conexión con el backend: {str(e)}"

    await update.message.reply_text(respuesta)  # Responde al usuario con la respuesta del backend

# Función principal que configura y ejecuta el bot
def main():
    print(f"🤖 Iniciando bot de Telegram...")
    print(f"   - TOKEN: {TOKEN[:10]}...")
    print(f"   - FASTAPI_URL: {FASTAPI_URL}")
    
    try:
        app = ApplicationBuilder().token(TOKEN).build()  # Crea la aplicación del bot con el token

        # Añade el handler para el comando /start
        app.add_handler(CommandHandler("start", start))
        # Añade el handler para mensajes de texto que no sean comandos
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        print("✅ Bot corriendo...")  # Mensaje en consola para indicar que el bot está activo
        
        # Configurar manejo de errores
        app.add_error_handler(error_handler)
        
        app.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True,  # Evitar conflictos con instancias anteriores
            close_loop=False
        )  # Inicia el polling para recibir mensajes
    except Exception as e:
        print(f"❌ Error al iniciar el bot: {e}")
        raise

async def error_handler(update, context):
    """Maneja errores del bot"""
    print(f"❌ Error en el bot: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("Lo siento, ocurrió un error. Inténtalo de nuevo.")

# Punto de entrada del script
if __name__ == "__main__":
    main()
