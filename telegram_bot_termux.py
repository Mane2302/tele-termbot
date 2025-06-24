#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Telegram avanzado para Termux con respuestas automáticas
Autor: Tu nombre
"""

import telebot
import time
import threading
import json
import os
from datetime import datetime

# ¡IMPORTANTE! Reemplaza 'TU_TOKEN_AQUI' con el token real de tu bot
BOT_TOKEN = ''

# Crear instancia del bot
bot = telebot.TeleBot(BOT_TOKEN)

# Variable para controlar el bot
bot_running = True

# Archivos de configuración
REPLIES_FILE = 'respuestas_auto.json'
CONFIG_FILE = 'config_bot.json'

# Cargar configuración
def load_config():
    """Cargar configuración del bot"""
    default_config = {
        'admin_users': [1143767637],
        'allowed_groups': [],
        'auto_replies_enabled': True,
        'bot_name': 'Mi Bot Personalizado'
    }
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            save_config(default_config)
            return default_config
    except:
        return default_config

def save_config(config):
    """Guardar configuración del bot"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando configuración: {e}")

# Cargar respuestas automáticas
def load_auto_replies():
    """Cargar respuestas automáticas desde archivo"""
    try:
        if os.path.exists(REPLIES_FILE):
            with open(REPLIES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except:
        return {}

def save_auto_replies(replies):
    """Guardar respuestas automáticas en archivo"""
    try:
        with open(REPLIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(replies, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error guardando respuestas: {e}")
        return False

# Variables globales
config = load_config()
auto_replies = load_auto_replies()

def is_admin(user_id):
    """Verificar si el usuario es administrador"""
    return user_id in config.get('admin_users', [])

def is_group_allowed(chat_id):
    """Verificar si el grupo está permitido"""
    allowed_groups = config.get('allowed_groups', [])
    return len(allowed_groups) == 0 or chat_id in allowed_groups

# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_type = "grupo" if message.chat.type in ['group', 'supergroup'] else "chat personal"
    
    welcome_text = f"""
🤖 ¡Hola {message.from_user.first_name}!

Soy **{config.get('bot_name', 'Mi Bot Personalizado')}** corriendo desde Termux.

📍 **Ubicación:** {chat_type}
🆔 **Chat ID:** `{message.chat.id}`
👤 **Tu ID:** `{message.from_user.id}`

**🔧 Comandos principales:**
/start - Mostrar este mensaje
/help - Ayuda completa
/config - Configuración del bot
/reply - Crear respuesta automática
/replies - Ver respuestas guardadas
/admin - Panel de administración

**💡 Respuestas Automáticas:**
Para crear una respuesta automática:
1️⃣ Envía un mensaje (texto, imagen, gif, sticker)
2️⃣ Responde a ese mensaje con: `/reply palabra_clave`
3️⃣ ¡Listo! El bot responderá cuando alguien diga esa palabra

Estado: {'🟢 Activo' if config.get('auto_replies_enabled', True) else '🔴 Desactivado'}
"""
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

# Comando /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
🤖 **GUÍA COMPLETA DEL BOT**

**📚 COMANDOS BÁSICOS:**
/start - Mensaje de bienvenida
/help - Esta guía completa
/hora - Hora actual del servidor
/info - Información del sistema
/ping - Verificar conexión

**⚙️ CONFIGURACIÓN:**
/config - Panel de configuración
/admin - Panel de administración (solo admins)

**🎯 RESPUESTAS AUTOMÁTICAS:**
/reply `palabra` - Crear respuesta (responder a un mensaje)
/replies - Ver todas las respuestas guardadas
/delreply `palabra` - Eliminar respuesta automática

**📖 CÓMO CREAR RESPUESTAS AUTOMÁTICAS:**

1️⃣ **Envía el contenido** que quieres que responda el bot:
   • Texto: "¡Hola! ¿Cómo estás?"
   • Imagen: Sube una foto
   • GIF: Sube un GIF
   • Sticker: Envía un sticker

2️⃣ **Responde a ese mensaje** con:
   `/reply palabra_clave`
   
   Ejemplo: `/reply hola`

3️⃣ **¡Listo!** Ahora cuando alguien escriba "hola", el bot enviará tu mensaje.

**💡 EJEMPLOS:**
• `/reply bienvenido` → Respuesta de bienvenida
• `/reply reglas` → Enviar reglas del grupo
• `/reply meme` → Enviar un meme gracioso
• `/reply info` → Información importante

**🔒 PERMISOS:**
• Cualquiera puede usar respuestas automáticas
• Solo admins pueden configurar el bot
• El bot funciona en grupos y chats privados

¿Necesitas ayuda con algo específico? ¡Pregunta!
"""
    bot.reply_to(message, help_text, parse_mode='Markdown')

# Comando /config
@bot.message_handler(commands=['config'])
def send_config(message):
    config_text = f"""
⚙️ **CONFIGURACIÓN DEL BOT**

**📊 Estado Actual:**
• **Nombre:** {config.get('bot_name', 'Mi Bot Personalizado')}
• **Respuestas Auto:** {'🟢 Activadas' if config.get('auto_replies_enabled', True) else '🔴 Desactivadas'}
• **Admins:** {len(config.get('admin_users', []))} usuarios
• **Grupos permitidos:** {len(config.get('allowed_groups', []))} grupos
• **Respuestas guardadas:** {len(auto_replies)} respuestas

**🆔 Información del Chat:**
• **Tipo:** {message.chat.type}
• **Chat ID:** `{message.chat.id}`
• **Tu ID:** `{message.from_user.id}`

**🔧 Para configurar el bot:**
• Usa /admin para panel de administración
• Añade tu ID como admin en el código
• Configura grupos permitidos
"""
    
    bot.reply_to(message, config_text, parse_mode='Markdown')

# Comando /admin
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ No tienes permisos de administrador.")
        return
    
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    # Botones del panel de admin
    btn_toggle = telebot.types.InlineKeyboardButton(
        "🔄 Toggle Respuestas", 
        callback_data="admin_toggle_replies"
    )
    btn_add_admin = telebot.types.InlineKeyboardButton(
        "👑 Añadir Admin", 
        callback_data="admin_add_admin"
    )
    btn_list_replies = telebot.types.InlineKeyboardButton(
        "📝 Ver Respuestas", 
        callback_data="admin_list_replies"
    )
    btn_clear_replies = telebot.types.InlineKeyboardButton(
        "🗑️ Limpiar Todo", 
        callback_data="admin_clear_replies"
    )
    
    keyboard.add(btn_toggle, btn_add_admin)
    keyboard.add(btn_list_replies, btn_clear_replies)
    
    admin_text = f"""
👑 **PANEL DE ADMINISTRACIÓN**

**Estado actual:**
• Respuestas automáticas: {'🟢 Activadas' if config.get('auto_replies_enabled', True) else '🔴 Desactivadas'}
• Total de respuestas: {len(auto_replies)}
• Admins registrados: {len(config.get('admin_users', []))}

Usa los botones para gestionar el bot:
"""
    
    bot.reply_to(message, admin_text, parse_mode='Markdown', reply_markup=keyboard)

# Manejador de callbacks para botones de admin
@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def handle_admin_callbacks(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Sin permisos")
        return
    
    global config, auto_replies
    
    if call.data == "admin_toggle_replies":
        config['auto_replies_enabled'] = not config.get('auto_replies_enabled', True)
        save_config(config)
        status = "activadas" if config['auto_replies_enabled'] else "desactivadas"
        bot.answer_callback_query(call.id, f"✅ Respuestas automáticas {status}")
        
    elif call.data == "admin_list_replies":
        if auto_replies:
            reply_list = "\n".join([f"• `{trigger}` → {info['type']}" for trigger, info in auto_replies.items()])
            bot.send_message(call.message.chat.id, f"📝 **Respuestas guardadas:**\n\n{reply_list}", parse_mode='Markdown')
        else:
            bot.send_message(call.message.chat.id, "📝 No hay respuestas automáticas guardadas.")
            
    elif call.data == "admin_clear_replies":
        auto_replies.clear()
        save_auto_replies(auto_replies)
        bot.answer_callback_query(call.id, "🗑️ Todas las respuestas eliminadas")

# Comando /reply para crear respuestas automáticas
@bot.message_handler(commands=['reply'])
def create_reply(message):
    global auto_replies
    
    # Verificar si es respuesta a un mensaje
    if not message.reply_to_message:
        bot.reply_to(message, """
❌ **Uso incorrecto**

Para crear una respuesta automática:

1️⃣ Envía un mensaje (texto, imagen, gif, etc.)
2️⃣ **Responde a ese mensaje** con: `/reply palabra_clave`

**Ejemplo:**
• Envías: "¡Bienvenido al grupo! 😊"
• Respondes con: `/reply bienvenida`
• Ahora cuando alguien diga "bienvenida", el bot enviará ese mensaje
""", parse_mode='Markdown')
        return
    
    # Obtener la palabra clave
    parts = message.text.split(' ', 1)
    if len(parts) < 2:
        bot.reply_to(message, "❌ Debes especificar una palabra clave: `/reply palabra_clave`", parse_mode='Markdown')
        return
    
    trigger = parts[1].lower().strip()
    
    if not trigger:
        bot.reply_to(message, "❌ La palabra clave no puede estar vacía.")
        return
    
    # Obtener el mensaje al que se está respondiendo
    reply_msg = message.reply_to_message
    chat_id = message.chat.id
    
    # Determinar el tipo de contenido
    content_info = {}
    
    if reply_msg.text:
        content_info = {
            'type': 'text',
            'content': reply_msg.text,
            'chat_id': chat_id
        }
    elif reply_msg.photo:
        content_info = {
            'type': 'photo',
            'file_id': reply_msg.photo[-1].file_id,
            'caption': reply_msg.caption or '',
            'chat_id': chat_id
        }
    elif reply_msg.animation:  # GIF
        content_info = {
            'type': 'animation',
            'file_id': reply_msg.animation.file_id,
            'caption': reply_msg.caption or '',
            'chat_id': chat_id
        }
    elif reply_msg.sticker:
        content_info = {
            'type': 'sticker',
            'file_id': reply_msg.sticker.file_id,
            'chat_id': chat_id
        }
    elif reply_msg.video:
        content_info = {
            'type': 'video',
            'file_id': reply_msg.video.file_id,
            'caption': reply_msg.caption or '',
            'chat_id': chat_id
        }
    elif reply_msg.document:
        content_info = {
            'type': 'document',
            'file_id': reply_msg.document.file_id,
            'caption': reply_msg.caption or '',
            'chat_id': chat_id
        }
    elif reply_msg.voice:
        content_info = {
            'type': 'voice',
            'file_id': reply_msg.voice.file_id,
            'chat_id': chat_id
        }
    else:
        bot.reply_to(message, "❌ Tipo de contenido no soportado.")
        return
    
    # Agregar información adicional
    content_info['created_by'] = message.from_user.id
    content_info['created_at'] = datetime.now().isoformat()
    content_info['chat_type'] = message.chat.type
    
    # Guardar la respuesta automática
    auto_replies[trigger] = content_info
    
    if save_auto_replies(auto_replies):
        bot.reply_to(message, f"""
✅ **Respuesta automática creada**

🔑 **Palabra clave:** `{trigger}`
📄 **Tipo:** {content_info['type']}
👤 **Creado por:** {message.from_user.first_name}

Ahora cuando alguien escriba "{trigger}", el bot enviará tu mensaje.

💡 **Prueba escribiendo:** {trigger}
""", parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ Error al guardar la respuesta automática.")

# Comando /replies para ver respuestas guardadas
@bot.message_handler(commands=['replies'])
def list_replies(message):
    if not auto_replies:
        bot.reply_to(message, """
📝 **No hay respuestas automáticas**

Para crear una:
1️⃣ Envía un mensaje
2️⃣ Responde con `/reply palabra_clave`

¡Así de fácil! 😊
""", parse_mode='Markdown')
        return
    
    reply_list = []
    for trigger, info in auto_replies.items():
        tipo = info['type']
        emoji = {
            'text': '📝',
            'photo': '🖼️',
            'animation': '🎞️',
            'sticker': '🎭',
            'video': '🎥',
            'document': '📎',
            'voice': '🎵'
        }.get(tipo, '📄')
        
        reply_list.append(f"{emoji} `{trigger}` → {tipo}")
    
    text = "📝 **Respuestas Automáticas Guardadas:**\n\n" + "\n".join(reply_list)
    text += f"\n\n**Total:** {len(auto_replies)} respuestas"
    text += "\n\n💡 Para eliminar: `/delreply palabra_clave`"
    
    bot.reply_to(message, text, parse_mode='Markdown')

# Comando /delreply para eliminar respuestas
@bot.message_handler(commands=['delreply'])
def delete_reply(message):
    global auto_replies
    
    parts = message.text.split(' ', 1)
    if len(parts) < 2:
        bot.reply_to(message, "❌ Especifica la palabra clave: `/delreply palabra_clave`", parse_mode='Markdown')
        return
    
    trigger = parts[1].lower().strip()
    
    if trigger in auto_replies:
        del auto_replies[trigger]
        save_auto_replies(auto_replies)
        bot.reply_to(message, f"✅ Respuesta automática `{trigger}` eliminada.", parse_mode='Markdown')
    else:
        bot.reply_to(message, f"❌ No existe una respuesta automática para `{trigger}`.", parse_mode='Markdown')

# Otros comandos básicos
@bot.message_handler(commands=['hora'])
def send_time(message):
    current_time = datetime.now().strftime("%H:%M:%S del %d/%m/%Y")
    bot.reply_to(message, f"🕐 **Hora actual:** {current_time}", parse_mode='Markdown')

@bot.message_handler(commands=['info'])
def send_info(message):
    import platform
    import os
    
    info_text = f"""
📱 **Información del Bot**


"""
    bot.reply_to(message, info_text, parse_mode='Markdown')

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "🏓 ¡Pong! Bot funcionando correctamente.")

# Comando /stop (solo para admins)
@bot.message_handler(commands=['stop'])
def stop_bot(message):
    global bot_running
    
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ No tienes permisos para detener el bot.")
        return
    
    bot.reply_to(message, "🛑 Deteniendo el bot...")
    bot_running = False
    bot.stop_polling()

# Manejador principal para respuestas automáticas
@bot.message_handler(func=lambda message: True)
def handle_auto_replies(message):
    # Mostrar información en consola
    chat_info = f"Grupo: {message.chat.title}" if message.chat.type in ['group', 'supergroup'] else "Chat privado"
    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
          f"{chat_info} | @{message.from_user.username} ({message.from_user.id}): {message.text}")
    
    # Verificar si las respuestas automáticas están habilitadas
    if not config.get('auto_replies_enabled', True):
        return
    
    # Verificar permisos de grupo
    if message.chat.type in ['group', 'supergroup'] and not is_group_allowed(message.chat.id):
        return
    
    # Solo procesar mensajes de texto para triggers
    if not message.text:
        return
    
    text_lower = message.text.lower()
    
    # Buscar coincidencias con triggers
    for trigger, reply_info in auto_replies.items():
        if trigger in text_lower:
            try:
                # Enviar respuesta según el tipo
                if reply_info['type'] == 'text':
                    bot.send_message(message.chat.id, reply_info['content'])
                elif reply_info['type'] == 'photo':
                    bot.send_photo(message.chat.id, reply_info['file_id'], caption=reply_info.get('caption', ''))
                elif reply_info['type'] == 'animation':
                    bot.send_animation(message.chat.id, reply_info['file_id'], caption=reply_info.get('caption', ''))
                elif reply_info['type'] == 'sticker':
                    bot.send_sticker(message.chat.id, reply_info['file_id'])
                elif reply_info['type'] == 'video':
                    bot.send_video(message.chat.id, reply_info['file_id'], caption=reply_info.get('caption', ''))
                elif reply_info['type'] == 'document':
                    bot.send_document(message.chat.id, reply_info['file_id'], caption=reply_info.get('caption', ''))
                elif reply_info['type'] == 'voice':
                    bot.send_voice(message.chat.id, reply_info['file_id'])
                
                print(f"🤖 Respuesta automática enviada: {trigger}")
                break  # Solo enviar una respuesta por mensaje
                
            except Exception as e:
                print(f"Error enviando respuesta automática: {e}")

# Función para mantener el bot vivo
def keep_alive():
    global bot_running
    while bot_running:
        try:
            print("🤖 Bot activo...")
            time.sleep(30)
        except KeyboardInterrupt:
            print("\n🛑 Bot detenido por el usuario")
            bot_running = False
            break

# Función principal
def main():
    global config
    
    print("🚀 Iniciando bot de Telegram avanzado...")
    print(f"📱 Bot: {config.get('bot_name', 'Mi Bot Personalizado')}")
    print(f"📊 Respuestas automáticas: {len(auto_replies)} cargadas")
    print(f"👑 Administradores: {len(config.get('admin_users', []))}")
    print("💡 Presiona Ctrl+C para detener")
    print("-" * 50)
    
    # Iniciar hilo para mantener vivo
    alive_thread = threading.Thread(target=keep_alive)
    alive_thread.daemon = True
    alive_thread.start()
    
    try:
        print("✅ Bot conectado y funcionando!")
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🛑 Bot desconectado.")

if __name__ == '__main__':
    main()