import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True  # Necesario para leer comandos

bot = commands.Bot(command_prefix=',', intents=intents)

REVIEWS_FILE = 'reviews.json'

# Carga de archivo
if os.path.exists(REVIEWS_FILE):
    with open(REVIEWS_FILE, 'r') as f:
        reviews = json.load(f)
else:
    reviews = {}

# ID del rol de staff
STAFF_ROLE_ID = 1368300606199959613

# Diccionario de roles automáticos por reseñas
roles_por_reseñas = {
    20: 1379860830967038063,  # Nivel 5️⃣
    15: 1379860733117993200,  # Nivel 4️⃣
    10: 1379860585768030339,  # Nivel 3️⃣
    5: 1379860513315618886,   # Nivel 2️⃣
    1: 1379860021160050801    # Nivel 1️⃣
}

def guardar_reviews():
    with open(REVIEWS_FILE, 'w') as f:
        json.dump(reviews, f)

def es_staff(member):
    return any(role.id == STAFF_ROLE_ID for role in member.roles)

async def actualizar_roles(usuario, guild, cantidad):
    # Primero quitar todos los roles de niveles que tenga
    for role_id in roles_por_reseñas.values():
        rol = guild.get_role(role_id)
        if rol and rol in usuario.roles:
            await usuario.remove_roles(rol)
    # Añadir el rol correcto según cantidad de reseñas
    for min_reseñas, role_id in sorted(roles_por_reseñas.items(), reverse=True):
        if cantidad >= min_reseñas:
            rol = guild.get_role(role_id)
            if rol:
                await usuario.add_roles(rol)
            break

@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def addreview(ctx, member: discord.Member = None, cantidad: int = 1):
    if member is None:
        await ctx.send("❌ Debes mencionar al usuario a quien quieres añadir reseñas.")
        return
    if es_staff(member) or member.bot:
        await ctx.send("❌ No puedes añadir reseñas a un staff o bot.")
        return

    uid = str(member.id)
    reviews[uid] = reviews.get(uid, 0) + cantidad
    guardar_reviews()

    await actualizar_roles(member, ctx.guild, reviews[uid])
    await ctx.send(f'✅ {cantidad} reseña(s) añadida(s) a {member.mention}. Total: {reviews[uid]}.')

@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def deletereview(ctx, member: discord.Member = None, cantidad: int = 1):
    if member is None:
        await ctx.send("❌ Debes mencionar al usuario a quien quieres quitar reseñas.")
        return
    if es_staff(member) or member.bot:
        await ctx.send("❌ No puedes quitar reseñas a un staff o bot.")
        return

    uid = str(member.id)
    reviews[uid] = max(0, reviews.get(uid, 0) - cantidad)
    guardar_reviews()

    await actualizar_roles(member, ctx.guild, reviews[uid])
    await ctx.send(f'✅ {cantidad} reseña(s) eliminada(s) de {member.mention}. Total: {reviews[uid]}.')

@bot.command()
async def reviewscount(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    uid = str(member.id)
    cantidad = reviews.get(uid, 0)
    await ctx.send(f'{member.mention} tiene {cantidad} reseña(s).')

@bot.command()
async def comandos(ctx):
    texto = (
        "**Lista de comandos disponibles:**\n\n"
        "`,addreview @usuario [cantidad]` - Añade reseñas al usuario mencionado. La cantidad es opcional y por defecto es 1.\n"
        "`,deletereview @usuario [cantidad]` - Quita reseñas al usuario mencionado. La cantidad es opcional y por defecto es 1.\n"
        "`,reviewscount [@usuario]` - Muestra cuántas reseñas tiene el usuario mencionado o a ti si no mencionas a nadie.\n"
        "`,comandos` - Muestra esta lista de comandos.\n\n"
        "**Nota:** Los comandos `addreview` y `deletereview` solo pueden ser usados por staff."
    )
    await ctx.send(texto)

@addreview.error
@deletereview.error
async def error_handler(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("❌ No tienes permiso para usar este comando.")
    else:
        await ctx.send(f"❌ Error inesperado: {error}")

print("Bot en marcha...")

load_dotenv()
bot.run(os.getenv("DISCORD_TOKEN"))
