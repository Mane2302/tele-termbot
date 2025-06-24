import os
import sys
import asyncio
import re
import subprocess
import yt_dlp
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# TOKEN CONFIGURADO
BOT_TOKEN = ""

# Directorio de descargas
DOWNLOAD_DIR = os.path.expanduser("~/storage/downloads/telegram_bot")
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def clean_filename(filename):
    """Limpia el nombre del archivo"""
    invalid_chars = '<>:"|?*/'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    filename = ' '.join(filename.split())
    return filename[:150].strip()

def ensure_storage_access():
    """Asegurar acceso al almacenamiento"""
    storage_path = os.path.expanduser("~/storage")
    return os.path.exists(storage_path)

def update_ytdlp():
    """Actualizar yt-dlp al iniciar"""
    try:
        logger.info("Actualizando yt-dlp...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], 
                      capture_output=True, check=True)
    except Exception as e:
        logger.error(f"Error actualizando yt-dlp: {e}")

update_ytdlp()

def download_video_sync(url_or_search, quality='360p', max_duration=1200):
    """Descargar video"""
    logger.info(f"Descargando video: {url_or_search}")
    
    download_dir = os.path.join(DOWNLOAD_DIR, "videos")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'user_agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36',
        'referer': 'https://www.youtube.com/',
        'http_headers': {
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },
        'geo_bypass': True,
        'nocheckcertificate': True,
        'socket_timeout': 90,
        'retries': 10,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if not url_or_search.startswith(('http://', 'https://')):
                info = ydl.extract_info(f"ytsearch:{url_or_search}", download=False)
                if info['entries']:
                    info = info['entries'][0]
                else:
                    return None, "No se encontraron resultados"
            else:
                info = ydl.extract_info(url_or_search, download=False)
        
        duration = info.get('duration', 0)
        if duration > max_duration:
            return None, f"Video muy largo: {duration//60} min (máx: {max_duration//60} min)"
        
        title = clean_filename(info.get('title', 'video'))
        video_path = os.path.join(download_dir, f"{title}.mp4")
        ydl_opts['outtmpl'] = video_path
        ydl_opts['format'] = 'best[height<=360][ext=mp4]/best[height<=360]/best'
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([info['webpage_url']])
        
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            if file_size > 50 * 1024 * 1024:
                os.remove(video_path)
                return None, "Archivo muy grande para Telegram (>50MB)"
            
            return video_path, {
                'title': info.get('title', 'video'),
                'duration': duration,
                'size': file_size / (1024 * 1024)
            }
        else:
            return None, "Error al descargar"
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return None, f"Error: {str(e)}"

def download_audio_sync(url_or_search, bitrate='128', max_duration=2400):
    """Descargar audio"""
    logger.info(f"Descargando audio: {url_or_search}")
    
    download_dir = os.path.join(DOWNLOAD_DIR, "music")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'user_agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36',
        'referer': 'https://www.youtube.com/',
        'http_headers': {
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },
        'geo_bypass': True,
        'nocheckcertificate': True,
        'socket_timeout': 30,
        'retries': 10,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if not url_or_search.startswith(('http://', 'https://')):
                info = ydl.extract_info(f"ytsearch:{url_or_search}", download=False)
                if info['entries']:
                    info = info['entries'][0]
                else:
                    return None, "No se encontraron resultados"
            else:
                info = ydl.extract_info(url_or_search, download=False)
        
        duration = info.get('duration', 0)
        if duration > max_duration:
            return None, f"Audio muy largo: {duration//60} min (máx: {max_duration//60} min)"
        
        title = clean_filename(info.get('title', 'audio'))
        artist = info.get('uploader', 'Unknown')
        audio_path = os.path.join(download_dir, f"{title}.mp3")
        ydl_opts['outtmpl'] = audio_path[:-4] + '.%(ext)s'
        ydl_opts['format'] = 'bestaudio/best'
        
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': bitrate,
            }]
        except:
            pass
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([info['webpage_url']])
        
        if os.path.exists(audio_path):
            final_path = audio_path
        else:
            for ext in ['.m4a', '.webm', '.opus', '.mp3']:
                test_path = audio_path[:-4] + ext
                if os.path.exists(test_path):
                    final_path = test_path
                    break
            else:
                return None, "Error al descargar"
        
        file_size = os.path.getsize(final_path)
        if file_size > 50 * 1024 * 1024:
            os.remove(final_path)
            return None, "Archivo muy grande para Telegram (>50MB)"
        
        return final_path, {
            'title': info.get('title', 'audio'),
            'artist': artist,
            'duration': duration,
            'size': file_size / (1024 * 1024)
        }
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return None, f"Error: {str(e)}"

# COMANDOS DEL BOT

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"¡Hola {user.first_name}! 👋\n\n"
        "Soy tu bot para descargar de YouTube.\n\n"
        "📹 /videoyt <URL o búsqueda> - Video (360p, máx 20 min)\n"
        "🎵 /musicyt <URL o búsqueda> - Audio (128kbps, máx 40 min)\n"
        "📊 /status - Ver estado del bot\n"
        "❓ /help - Mostrar ayuda"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    await update.message.reply_text(
        "📚 **Cómo usar el bot:**\n\n"
        "**Para videos:**\n"
        "`/videoyt https://youtube.com/watch?v=...`\n"
        "`/videoyt nombre del video`\n\n"
        "**Para música:**\n"
        "`/musicyt nombre de la canción`\n"
        "`/musicyt artista - canción`\n\n"
        "**Límites:**\n"
        "• Videos: 360p, máx 20 minutos\n"
        "• Audio: 128kbps, máx 40 minutos\n"
        "• Tamaño: máx 50MB (límite de Telegram)",
        parse_mode='Markdown'
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status"""
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        ytdlp_version = result.stdout.strip() if result.returncode == 0 else "Error"
    except:
        ytdlp_version = "No instalado"
    
    status_msg = (
        "📊 **Estado del Bot**\n\n"
        f"🤖 Bot: ✅ Activo\n"
        f"📥 yt-dlp: {ytdlp_version}\n"
        f"💾 Almacenamiento: {'✅' if ensure_storage_access() else '❌'}"
    )
    
    await update.message.reply_text(status_msg, parse_mode='Markdown')

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /videoyt"""
    if not context.args:
        await update.message.reply_text("❌ Uso: /videoyt <URL o búsqueda>")
        return
    
    query = ' '.join(context.args)
    msg = await update.message.reply_text("🔍 Buscando video...")
    
    try:
        loop = asyncio.get_event_loop()
        video_path, result = await loop.run_in_executor(
            None, download_video_sync, query, '360p', 1200
        )
        
        if video_path:
            await msg.edit_text(f"📤 Enviando: {result['title'][:30]}...")
            
            with open(video_path, 'rb') as video:
                await update.message.reply_video(
                    video=video,
                    caption=f"🎬 {result['title']}",
                    supports_streaming=True
                )
            
            os.remove(video_path)
            await msg.delete()
        else:
            await msg.edit_text(f"❌ {result}")
            
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

async def download_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /musicyt"""
    if not context.args:
        await update.message.reply_text("❌ Uso: /musicyt <URL o búsqueda>")
        return
    
    query = ' '.join(context.args)
    msg = await update.message.reply_text("🔍 Buscando música...")
    
    try:
        loop = asyncio.get_event_loop()
        audio_path, result = await loop.run_in_executor(
            None, download_audio_sync, query, '128', 2400
        )
        
        if audio_path:
            await msg.edit_text(f"📤 Enviando: {result['title'][:30]}...")
            
            with open(audio_path, 'rb') as audio:
                await update.message.reply_audio(
                    audio=audio,
                    caption=f"🎵 {result['title']}",
                    title=result['title'],
                    performer=result['artist']
                )
            
            os.remove(audio_path)
            await msg.delete()
        else:
            await msg.edit_text(f"❌ {result}")
            
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador de errores"""
    logger.error(f"Error: {context.error}")
    if update and update.message:
        await update.message.reply_text("❌ Error procesando tu solicitud")

def main():
    """Función principal"""
    print("🤖 Bot de Telegram iniciando...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("videoyt", download_video))
    application.add_handler(CommandHandler("musicyt", download_music))
    
    application.add_error_handler(error_handler)
    
    print("✅ Bot iniciado! Presiona Ctrl+C para detener")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Bot detenido")
    except Exception as e:
        print(f"❌ Error: {e}")