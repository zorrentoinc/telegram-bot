from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

# ⚙️ Configuración
TOKEN = "7262942819:AAFZrE-TmVPTPZgw84dkDhq0qHMKr6wMjwI"  # ← Reemplaza con tu token real
CLAVE_ACCESO = "tyoxdd"
RUTA_BASE = "cuentas"

# Servicios disponibles
SERVICIOS = ["disney", "hbo", "crunchy", "paramount"]

# Usuarios que ya ingresaron la clave
usuarios_autenticados = set()

# Crear carpeta si no existe
if not os.path.exists(RUTA_BASE):
    os.makedirs(RUTA_BASE)

# 📩 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bienvenido. Por favor envíame la clave de acceso para continuar.")

# 🔐 Validación de clave
async def mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    texto = update.message.text.strip().lower()

    if user_id not in usuarios_autenticados:
        if texto == CLAVE_ACCESO:
            usuarios_autenticados.add(user_id)
            await update.message.reply_text("✅ Acceso concedido.\n\nUsa /get [servicio] (ej: /get disney)\nO /stock para ver disponibilidad.")
        else:
            await update.message.reply_text("❌ Clave incorrecta.")
    else:
        await update.message.reply_text("🔐 Ya estás autenticado. Usa /get servicio (ej: /get hbo)")

# 🎁 /get [servicio]
async def get_cuenta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in usuarios_autenticados:
        await update.message.reply_text("🔒 Primero debes enviar la clave de acceso.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("❗ Usa el comando así: /get servicio (disney, hbo, crunchy, paramount)")
        return

    servicio = context.args[0].lower()

    if servicio not in SERVICIOS:
        await update.message.reply_text("⚠️ Servicio no válido. Opciones: disney, hbo, crunchy, paramount.")
        return

    archivo_servicio = os.path.join(RUTA_BASE, f"{servicio}.txt")
    archivo_entregadas = os.path.join(RUTA_BASE, f"entregadas_{servicio}.txt")

    if not os.path.exists(archivo_servicio):
        await update.message.reply_text("❌ Archivo de servicio no encontrado.")
        return

    with open(archivo_servicio, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    if not lineas:
        await update.message.reply_text(f"🚫 No hay más cuentas de {servicio} disponibles.")
        return

    cuenta = lineas[0].strip()

    # Guardar como entregada
    with open(archivo_entregadas, "a", encoding="utf-8") as f:
        f.write(cuenta + "\n")

    # Eliminar del original
    with open(archivo_servicio, "w", encoding="utf-8") as f:
        f.writelines(lineas[1:])

    await update.message.reply_text(f"🎁 Tu cuenta de {servicio}:\n\n`{cuenta}`", parse_mode="Markdown")

# 📦 /stock
async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in usuarios_autenticados:
        await update.message.reply_text("🔒 Primero debes enviar la clave de acceso.")
        return

    mensaje = "📦 *Stock actual:*\n\n"

    for servicio in SERVICIOS:
        archivo_cuentas = os.path.join(RUTA_BASE, f"{servicio}.txt")
        archivo_entregadas = os.path.join(RUTA_BASE, f"entregadas_{servicio}.txt")

        disponibles = 0
        entregadas = 0

        if os.path.exists(archivo_cuentas):
            with open(archivo_cuentas, "r", encoding="utf-8") as f:
                disponibles = len(f.readlines())

        if os.path.exists(archivo_entregadas):
            with open(archivo_entregadas, "r", encoding="utf-8") as f:
                entregadas = len(f.readlines())

        emoji = {
            "disney": "🟥",
            "hbo": "🟦",
            "crunchy": "🟨",
            "paramount": "🟪"
        }.get(servicio, "📌")

        mensaje += f"{emoji} *{servicio.capitalize()}*: {disponibles} disponibles, {entregadas} entregadas\n"

    await update.message.reply_text(mensaje, parse_mode="Markdown")

# 🚀 Inicio del bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("get", get_cuenta))
    app.add_handler(CommandHandler("stock", stock))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje))

    print("🤖 Bot ejecutándose...")
    app.run_polling()

if __name__ == "__main__":
    main()
