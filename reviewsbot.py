import discord
from discord.ext import commands
import json
import os

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
    for role_id in roles_por_reseñas.values():
        rol = guild.get_role(role_id)
        if rol and rol in usuario.roles:
            await usuario.remove_roles(rol)
    for min_reseñas, role_id in sorted(roles_por_reseñas.items(), reverse=True):
        if cantidad >= min_reseñas:
            rol = guild.get_role(role_id)
            if rol:
                await usuario.add_roles(rol)
            break

def encontrar_usuario_valido(ctx):
    usuarios_validos = []
    for member in ctx.channel.members:
        if not member.bot and not es_staff(member):
            usuarios_validos.append(member)
    return usuarios_validos

@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def addreview(ctx, cantidad: int = 1):
    candidatos = encontrar_usuario_valido(ctx)
    if len(candidatos) == 0:
        await ctx.send("❌ No hay usuarios válidos en este canal.")
        return
    if len(candidatos) > 1:
        await ctx.send("❌ Hay más de un usuario válido, no sé a quién añadir reseñas.")
        return

    usuario = candidatos[0]
    uid = str(usuario.id)
    reviews[uid] = reviews.get(uid, 0) + cantidad
    guardar_reviews()

    await actualizar_roles(usuario, ctx.guild, reviews[uid])
    await ctx.send(f'✅ {cantidad} reseña(s) añadida(s) a {usuario.mention}. Total: {reviews[uid]}.')

@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def deletereview(ctx, cantidad: int = 1):
    candidatos = encontrar_usuario_valido(ctx)
    if len(candidatos) == 0:
        await ctx.send("❌ No hay usuarios válidos en este canal.")
        return
    if len(candidatos) > 1:
        await ctx.send("❌ Hay más de un usuario válido, no sé a quién quitar reseñas.")
        return

    usuario = candidatos[0]
    uid = str(usuario.id)
    reviews[uid] = max(0, reviews.get(uid, 0) - cantidad)
    guardar_reviews()

    await actualizar_roles(usuario, ctx.guild, reviews[uid])
    await ctx.send(f'✅ {cantidad} reseña(s) eliminada(s) de {usuario.mention}. Total: {reviews[uid]}.')

@bot.command()
async def reviewscount(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    uid = str(member.id)
    cantidad = reviews.get(uid, 0)
    await ctx.send(f'{member.mention} tiene {cantidad} reseña(s).')

@addreview.error
@deletereview.error
async def error_handler(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("❌ No tienes permiso para usar este comando.")
    else:
        await ctx.send(f"❌ Error inesperado: {error}")

print("Bot en marcha...")
from dotenv import load_dotenv
import os

load_dotenv()
bot.run(os.getenv("DISCORD_TOKEN"))