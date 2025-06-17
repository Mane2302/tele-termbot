#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Telegram simple para Termux
Autor: Tu nombre
"""

import telebot
import time
import threading
from datetime import datetime

# ¡IMPORTANTE! Reemplaza 'TU_TOKEN_AQUI' con el token real de tu bot
BOT_TOKEN = 'TU_TOKEN_AQUI'

# Crear instancia del bot
bot = telebot.TeleBot(BOT_TOKEN)

# Variable para controlar el bot
bot_running = True

# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = f"""
¡Hola {message.from_user.first_name}! 👋

Soy un bot simple corriendo desde Termux.

Comandos disponibles:
/start - Mostrar este mensaje
/help - Ayuda
/hora - Hora actual
/info - Información del bot
/stop - Detener bot (solo admin)

¡Escríbeme cualquier mensaje y te responderé!
"""
    bot.reply_to(message, welcome_text)

# Comando /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
🤖 **Ayuda del Bot**

**Comandos:**
/start - Mensaje de bienvenida
/help - Esta ayuda
/hora - Muestra la hora actual
/info - Información del sistema
/stop - Detener el bot

**Funciones:**
- Responde a cualquier mensaje de texto
- Eco de mensajes
- Comandos básicos

¿Necesitas algo más? ¡Solo pregunta!
"""
    bot.reply_to(message, help_text, parse_mode='Markdown')

# Comando /hora
@bot.message_handler(commands=['hora'])
def send_time(message):
    current_time = datetime.now().strftime("%H:%M:%S del %d/%m/%Y")
    bot.reply_to(message, f"🕐 Hora actual: {current_time}")

# Comando /info
@bot.message_handler(commands=['info'])
def send_info(message):
    import platform
    import os
    
    info_text = f"""
📱 **Información del Bot**

**Sistema:** {platform.system()}
**Versión Python:** {platform.python_version()}
**Usuario:** {os.getenv('USER', 'Desconocido')}
**Directorio:** {os.getcwd()}

🤖 Bot corriendo desde Termux en Android
"""
    bot.reply_to(message, info_text, parse_mode='Markdown')

# Comando /stop (solo para el creador del bot)
@bot.message_handler(commands=['stop'])
def stop_bot(message):
    global bot_running
    
    # Aquí puedes poner tu user_id para que solo tú puedas detener el bot
    # Para obtener tu user_id, envía cualquier mensaje y revisa los logs
    admin_ids = [message.from_user.id]  # Por ahora, cualquiera puede detenerlo
    
    if message.from_user.id in admin_ids:
        bot.reply_to(message, "🛑 Deteniendo el bot...")
        bot_running = False
        bot.stop_polling()
    else:
        bot.reply_to(message, "❌ No tienes permisos para detener el bot.")

# Manejador para todos los mensajes de texto
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    # Mostrar información del mensaje en la consola
    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
          f"Usuario: @{message.from_user.username} ({message.from_user.id}) "
          f"Mensaje: {message.text}")
    
    # Respuestas automáticas
    if "hola" in message.text.lower():
        bot.reply_to(message, f"¡Hola {message.from_user.first_name}! 😊")
    elif "gracias" in message.text.lower():
        bot.reply_to(message, "¡De nada! 😄")
    elif "bot" in message.text.lower():
        bot.reply_to(message, "¡Sí, soy un bot! 🤖 ¿En qué puedo ayudarte?")
    else:
        # Eco simple
        bot.reply_to(message, f"Recibí tu mensaje: {message.text}")

# Función para mantener el bot vivo
def keep_alive():
    while bot_running:
        try:
            print("🤖 Bot activo...")
            time.sleep(30)  # Mensaje cada 30 segundos
        except KeyboardInterrupt:
            print("\n🛑 Bot detenido por el usuario")
            global bot_running
            bot_running = False
            break

# Función principal
def main():
    print("🚀 Iniciando bot de Telegram...")
    print(f"📱 Bot corriendo desde Termux")
    print("💡 Presiona Ctrl+C para detener")
    print("-" * 40)
    
    # Iniciar hilo para mantener vivo
    alive_thread = threading.Thread(target=keep_alive)
    alive_thread.daemon = True
    alive_thread.start()
    
    try:
        # Iniciar el bot
        print("✅ Bot conectado y funcionando!")
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🛑 Bot desconectado.")

if __name__ == '__main__':
    main()