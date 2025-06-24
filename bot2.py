#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import telebot
import time
import threading
import json
import os
from datetime import datetime, timedelta
import signal
import sys

# ¡IMPORTANTE! Reemplaza 'TU_TOKEN_AQUI' con el token real de tu bot
BOT_TOKEN = ''

# Crear instancia del bot
bot = telebot.TeleBot(BOT_TOKEN)

# Variable para controlar el bot
bot_running = True
should_stop = False  # Nueva variable para detener completamente el bot

# Archivos de configuración
REPLIES_FILE = 'respuestas_auto.json'
CONFIG_FILE = 'config_bot.json'
ACTIVITY_FILE = 'user_activity.json'

# Cargar configuración
def load_config():
    """Cargar configuración del bot"""
    default_config = {
        'admin_users': [1143767637],
        'allowed_groups': [],
        'auto_replies_enabled': True,
        'bot_name': 'Mi Bot Personalizado',
        'inactivity_days': 30  # Días para considerar a un usuario inactivo
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

# Funciones para el tracking de actividad de usuarios
def load_user_activity():
    """Cargar actividad de usuarios desde archivo"""
    try:
        if os.path.exists(ACTIVITY_FILE):
            with open(ACTIVITY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except:
        return {}

def save_user_activity(activity):
    """Guardar actividad de usuarios en archivo"""
    try:
        with open(ACTIVITY_FILE, 'w', encoding='utf-8') as f:
            json.dump(activity, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error guardando actividad de usuarios: {e}")
        return False

def update_user_activity(user_id, chat_id, username, first_name):
    """Actualizar la última actividad de un usuario"""
    global user_activity
    
    # Crear key único para cada usuario en cada grupo
    key = f"{chat_id}_{user_id}"
    
    user_activity[key] = {
        'user_id': user_id,
        'chat_id': chat_id,
        'username': username,
        'first_name': first_name,
        'last_activity': datetime.now().isoformat(),
        'message_count': user_activity.get(key, {}).get('message_count', 0) + 1
    }
    
    save_user_activity(user_activity)

# Variables globales
config = load_config()
auto_replies = load_auto_replies()
user_activity = load_user_activity()

def is_admin(user_id):
    """Verificar si el usuario es administrador"""
    return user_id in config.get('admin_users', [])

def is_group_allowed(chat_id):
    """Verificar si el grupo está permitido"""
    allowed_groups = config.get('allowed_groups', [])
    return len(allowed_groups) == 0 or chat_id in allowed_groups

def is_bot_admin(chat_id):
    """Verificar si el bot es administrador en el grupo"""
    try:
        bot_member = bot.get_chat_member(chat_id, bot.get_me().id)
        return bot_member.status in ['administrator', 'creator']
    except:
        return False

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
/inactivesca - Ver usuarios inactivos (admin)

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
/inactivesca - Control de usuarios inactivos (solo admins)

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

**🔒 PERMISOS:**
• Cualquiera puede usar respuestas automáticas
• Solo admins pueden configurar el bot
• El bot funciona en grupos y chats privados

¿Necesitas ayuda con algo específico? ¡Pregunta!
"""
    bot.reply_to(message, help_text, parse_mode='Markdown')

# Comando /inactivesca - Ver usuarios inactivos
@bot.message_handler(commands=['inactivesca'])
def show_inactive_users(message):
    # Verificar si es admin
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ No tienes permisos de administrador.")
        return
    
    # Verificar si es en un grupo
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "❌ Este comando solo funciona en grupos.")
        return
    
    # Verificar si el bot es admin en el grupo
    if not is_bot_admin(message.chat.id):
        bot.reply_to(message, "❌ El bot necesita ser administrador del grupo para usar esta función.")
        return
    
    chat_id = message.chat.id
    inactivity_days = config.get('inactivity_days', 30)
    cutoff_date = datetime.now() - timedelta(days=inactivity_days)
    
    # Filtrar usuarios inactivos de este grupo
    inactive_users = []
    for key, user_data in user_activity.items():
        if str(user_data['chat_id']) == str(chat_id):
            last_activity = datetime.fromisoformat(user_data['last_activity'])
            if last_activity < cutoff_date:
                days_inactive = (datetime.now() - last_activity).days
                inactive_users.append({
                    'user_id': user_data['user_id'],
                    'username': user_data.get('username', 'Sin username'),
                    'first_name': user_data.get('first_name', 'Usuario'),
                    'days_inactive': days_inactive,
                    'last_activity': last_activity.strftime('%d/%m/%Y')
                })
    
    if not inactive_users:
        bot.reply_to(message, f"✅ No hay usuarios inactivos en los últimos {inactivity_days} días.")
        return
    
    # Ordenar por días de inactividad
    inactive_users.sort(key=lambda x: x['days_inactive'], reverse=True)
    
    # Crear mensaje con lista de inactivos
    text = f"👥 **USUARIOS INACTIVOS** (más de {inactivity_days} días)\n\n"
    
    for i, user in enumerate(inactive_users[:10]):  # Mostrar máximo 10
        text += f"{i+1}. **{user['first_name']}**\n"
        text += f"   • Username: @{user['username']}\n" if user['username'] != 'Sin username' else ""
        text += f"   • Inactivo: {user['days_inactive']} días\n"
        text += f"   • Última vez: {user['last_activity']}\n\n"
    
    if len(inactive_users) > 10:
        text += f"\n... y {len(inactive_users) - 10} usuarios más."
    
    # Crear botones de acción
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    btn_ban_all = telebot.types.InlineKeyboardButton(
        "🚫 Banear todos", 
        callback_data=f"inactive_ban_all_{chat_id}"
    )
    btn_mute_all = telebot.types.InlineKeyboardButton(
        "🔇 Silenciar todos", 
        callback_data=f"inactive_mute_all_{chat_id}"
    )
    btn_settings = telebot.types.InlineKeyboardButton(
        "⚙️ Configurar días", 
        callback_data="inactive_settings"
    )
    btn_refresh = telebot.types.InlineKeyboardButton(
        "🔄 Actualizar", 
        callback_data="inactive_refresh"
    )
    
    keyboard.add(btn_ban_all, btn_mute_all)
    keyboard.add(btn_settings, btn_refresh)
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=keyboard)

# Manejador de callbacks para usuarios inactivos
@bot.callback_query_handler(func=lambda call: call.data.startswith('inactive_'))
def handle_inactive_callbacks(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Sin permisos")
        return
    
    data_parts = call.data.split('_')
    action = data_parts[1]
    
    if action == 'ban' and data_parts[2] == 'all':
        chat_id = data_parts[3]
        count = ban_inactive_users(chat_id)
        bot.answer_callback_query(call.id, f"✅ {count} usuarios baneados")
        bot.edit_message_text(
            f"✅ Se han baneado {count} usuarios inactivos.",
            call.message.chat.id,
            call.message.message_id
        )
        
    elif action == 'mute' and data_parts[2] == 'all':
        chat_id = data_parts[3]
        count = mute_inactive_users(chat_id)
        bot.answer_callback_query(call.id, f"✅ {count} usuarios silenciados")
        bot.edit_message_text(
            f"✅ Se han silenciado {count} usuarios inactivos por 24 horas.",
            call.message.chat.id,
            call.message.message_id
        )
        
    elif action == 'settings':
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
        for days in [7, 14, 30, 60, 90]:
            btn = telebot.types.InlineKeyboardButton(
                f"{days} días",
                callback_data=f"inactive_setdays_{days}"
            )
            keyboard.add(btn)
        
        bot.edit_message_text(
            "⚙️ **Configurar días de inactividad**\n\nSelecciona después de cuántos días considerar a un usuario como inactivo:",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        
    elif action == 'setdays':
        days = int(data_parts[2])
        config['inactivity_days'] = days
        save_config(config)
        bot.answer_callback_query(call.id, f"✅ Configurado a {days} días")
        bot.edit_message_text(
            f"✅ Ahora se considerarán inactivos los usuarios sin actividad en {days} días.",
            call.message.chat.id,
            call.message.message_id
        )
        
    elif action == 'refresh':
        # Refrescar la lista
        show_inactive_users(call.message)
        bot.delete_message(call.message.chat.id, call.message.message_id)

def ban_inactive_users(chat_id):
    """Banear usuarios inactivos de un grupo"""
    inactivity_days = config.get('inactivity_days', 30)
    cutoff_date = datetime.now() - timedelta(days=inactivity_days)
    banned_count = 0
    
    for key, user_data in user_activity.items():
        if str(user_data['chat_id']) == str(chat_id):
            last_activity = datetime.fromisoformat(user_data['last_activity'])
            if last_activity < cutoff_date:
                try:
                    bot.ban_chat_member(chat_id, user_data['user_id'])
                    banned_count += 1
                except Exception as e:
                    print(f"Error baneando usuario {user_data['user_id']}: {e}")
    
    return banned_count

def mute_inactive_users(chat_id):
    """Silenciar usuarios inactivos por 24 horas"""
    inactivity_days = config.get('inactivity_days', 30)
    cutoff_date = datetime.now() - timedelta(days=inactivity_days)
    muted_count = 0
    
    # Permisos de silenciado (no puede enviar mensajes)
    permissions = telebot.types.ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_change_info=False,
        can_invite_users=False,
        can_pin_messages=False
    )
    
    for key, user_data in user_activity.items():
        if str(user_data['chat_id']) == str(chat_id):
            last_activity = datetime.fromisoformat(user_data['last_activity'])
            if last_activity < cutoff_date:
                try:
                    # Silenciar por 24 horas
                    until_date = int(time.time()) + (24 * 60 * 60)
                    bot.restrict_chat_member(
                        chat_id, 
                        user_data['user_id'],
                        permissions=permissions,
                        until_date=until_date
                    )
                    muted_count += 1
                except Exception as e:
                    print(f"Error silenciando usuario {user_data['user_id']}: {e}")
    
    return muted_count

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
• **Días inactividad:** {config.get('inactivity_days', 30)} días

**🆔 Información del Chat:**
• **Tipo:** {message.chat.type}
• **Chat ID:** `{message.chat.id}`
• **Tu ID:** `{message.from_user.id}`

**🔧 Para configurar el bot:**
• Usa /admin para panel de administración
• Usa /inactivesca para control de usuarios
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
    btn_inactive = telebot.types.InlineKeyboardButton(
        "👥 Usuarios Inactivos", 
        callback_data="admin_show_inactive"
    )
    btn_stats = telebot.types.InlineKeyboardButton(
        "📊 Estadísticas", 
        callback_data="admin_stats"
    )
    
    keyboard.add(btn_toggle, btn_add_admin)
    keyboard.add(btn_list_replies, btn_clear_replies)
    keyboard.add(btn_inactive, btn_stats)
    
    admin_text = f"""
👑 **PANEL DE ADMINISTRACIÓN**

**Estado actual:**
• Respuestas automáticas: {'🟢 Activadas' if config.get('auto_replies_enabled', True) else '🔴 Desactivadas'}
• Total de respuestas: {len(auto_replies)}
• Admins registrados: {len(config.get('admin_users', []))}
• Usuarios rastreados: {len(user_activity)}

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
        
    elif call.data == "admin_show_inactive":
        show_inactive_users(call.message)
        
    elif call.data == "admin_stats":
        total_users = len(user_activity)
        active_7d = sum(1 for user in user_activity.values() 
                       if (datetime.now() - datetime.fromisoformat(user['last_activity'])).days <= 7)
        active_30d = sum(1 for user in user_activity.values() 
                        if (datetime.now() - datetime.fromisoformat(user['last_activity'])).days <= 30)
        
        stats_text = f"""
📊 **ESTADÍSTICAS DEL BOT**

**👥 Usuarios:**
• Total rastreados: {total_users}
• Activos (7 días): {active_7d}
• Activos (30 días): {active_30d}
• Inactivos: {total_users - active_30d}

**💬 Respuestas automáticas:**
• Total guardadas: {len(auto_replies)}
• Estado: {'🟢 Activas' if config.get('auto_replies_enabled', True) else '🔴 Inactivas'}

**⚙️ Configuración:**
• Días para inactividad: {config.get('inactivity_days', 30)}
• Admins: {len(config.get('admin_users', []))}
"""
        bot.send_message(call.message.chat.id, stats_text, parse_mode='Markdown')

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
    
    info_text = f"""
📱 **Información del Bot**

• **Sistema:** {platform.system()} {platform.release()}
• **Python:** {platform.python_version()}
• **Bot activo desde:** {bot_start_time}
• **Reconexiones:** {reconnect_count}
    """
    bot.reply_to(message, info_text, parse_mode='Markdown')

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "🏓 ¡Pong! Bot funcionando correctamente.")

# Comando /stop (solo para admins)
@bot.message_handler(commands=['stop'])
def stop_bot(message):
    global bot_running, should_stop
    
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ No tienes permisos para detener el bot.")
        return
    
    bot.reply_to(message, "🛑 Deteniendo el bot completamente...")
    bot_running = False
    should_stop = True  # Esto evitará que se reconecte
    bot.stop_polling()

# Manejador principal para respuestas automáticas
@bot.message_handler(func=lambda message: True)
def handle_auto_replies(message):
    # Actualizar actividad del usuario si es en un grupo
    if message.chat.type in ['group', 'supergroup']:
        update_user_activity(
            message.from_user.id,
            message.chat.id,
            message.from_user.username,
            message.from_user.first_name
        )
    
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

# Función para manejar la señal de interrupción
def signal_handler(sig, frame):
    global should_stop
    print("\n🛑 Interrupción detectada. Deteniendo bot...")
    should_stop = True
    sys.exit(0)

# Función para mantener el bot vivo
def keep_alive():
    global bot_running
    while bot_running and not should_stop:
        try:
            print("🤖 Bot activo...")
            time.sleep(30)
        except KeyboardInterrupt:
            print("\n🛑 Bot detenido por el usuario")
            break

# Variables para estadísticas
bot_start_time = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
reconnect_count = 0

# Función principal con reconexión automática
def main():
    global config, bot_running, should_stop, reconnect_count
    
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🚀 Iniciando bot de Telegram avanzado con reconexión automática...")
    print(f"📱 Bot: {config.get('bot_name', 'Mi Bot Personalizado')}")
    print(f"📊 Respuestas automáticas: {len(auto_replies)} cargadas")
    print(f"👑 Administradores: {len(config.get('admin_users', []))}")
    print("💡 Presiona Ctrl+C para detener")
    print("-" * 50)
    
    # Bucle principal con reconexión automática
    while not should_stop:
        try:
            # Iniciar hilo para mantener vivo
            alive_thread = threading.Thread(target=keep_alive)
            alive_thread.daemon = True
            alive_thread.start()
            
            print(f"✅ Bot conectado y funcionando! (Reconexiones: {reconnect_count})")
            bot_running = True
            bot.polling(none_stop=True, interval=0, timeout=20)
            
        except KeyboardInterrupt:
            print("\n🛑 Bot detenido manualmente por el usuario.")
            should_stop = True
            break
            
        except Exception as e:
            if not should_stop:
                reconnect_count += 1
                wait_time = min(30 * reconnect_count, 300)  # Máximo 5 minutos
                print(f"❌ Error de conexión: {e}")
                print(f"🔄 Intentando reconectar en {wait_time} segundos... (Intento #{reconnect_count})")
                
                # Esperar antes de reconectar
                for i in range(wait_time):
                    if should_stop:
                        break
                    time.sleep(1)
                
                if not should_stop:
                    print("🔄 Reconectando...")
            else:
                break
    
    print("🛑 Bot completamente detenido.")

if __name__ == '__main__':
    main()