import discord
from discord.ext import commands
from discord import app_commands
import os
import random

# ⚙️ CONFIG

TOKEN = os.getenv(“TOKEN”)
ROLE_MEMBRE_ID = 1476761476508155974
team_roles = {}  # Liaisons manuelles catégorie -> rôle

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=”!”, intents=intents)

GUILD_ID = 1476624785524920332

@bot.event
async def on_ready():
guild = discord.Object(id=GUILD_ID)
bot.tree.copy_global_to(guild=guild)
synced = await bot.tree.sync(guild=guild)
print(f”✅ Bot connecté en tant que {bot.user}”)
print(f”✅ {len(synced)} commandes synchronisées !”)
activity = discord.Activity(
type=discord.ActivityType.playing,
name=“UraCraft”,
details=“Chill”,
)
await bot.change_presence(status=discord.Status.online, activity=activity)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🔗 invite — Sans préfixe

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.event
async def on_message(message):
if message.author.bot:
return
if message.content.lower() == “invite”:
await message.channel.send(“🔗 Rejoins UraCraft ici : https://discord.gg/V3S5QfQdkD”)
await bot.process_commands(message)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ⭐ /team-setup

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“team-setup”, description=“Crée la catégorie, les salons et le rôle de la team”)
@app_commands.describe(nom=“Nom de la team”, emoji=“Emoji (laisse vide pour ⭐)”)
@app_commands.checks.has_permissions(administrator=True)
async def team_setup(interaction: discord.Interaction, nom: str, emoji: str = “⭐”):
guild = interaction.guild
await interaction.response.defer()
role = await guild.create_role(name=f”{emoji} {nom}”, color=discord.Color.gold(), mentionable=True)
role_membre = guild.get_role(ROLE_MEMBRE_ID)
category = await guild.create_category(f”{emoji} {nom}”)
overwrites_prive = {
guild.default_role: discord.PermissionOverwrite(view_channel=False),
role: discord.PermissionOverwrite(view_channel=True)
}
overwrites_rejoindre = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
if role_membre:
overwrites_rejoindre[role_membre] = discord.PermissionOverwrite(view_channel=True)
else:
overwrites_rejoindre[guild.default_role] = discord.PermissionOverwrite(view_channel=True)
await guild.create_text_channel(f”{emoji}•pour-rejoindre”, category=category, overwrites=overwrites_rejoindre)
await guild.create_text_channel(f”{emoji}•général•💬”, category=category, overwrites=overwrites_prive)
annonce = await guild.create_text_channel(f”{emoji}•annonce•📣”, category=category, overwrites=overwrites_prive)
await annonce.edit(type=discord.ChannelType.news)
await guild.create_voice_channel(f”{emoji}•Voc•🔊”, category=category, overwrites=overwrites_prive)
await interaction.followup.send(f”✅ Team **{nom}** créée !\n📁 Catégorie : `{emoji} {nom}`\n🎭 Rôle : `{emoji} {nom}`”)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🗑️ /team-supp

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“team-supp”, description=“Supprime la catégorie, les salons et le rôle de la team”)
@app_commands.describe(nom=“Nom de la team à supprimer”)
@app_commands.checks.has_permissions(administrator=True)
async def team_supp(interaction: discord.Interaction, nom: str):
guild = interaction.guild
await interaction.response.defer()
supprime, erreurs = [], []
category = next((c for c in guild.categories if nom.lower() in c.name.lower()), None)
if category:
for channel in category.channels:
await channel.delete()
await category.delete()
supprime.append(f”📁 Catégorie `{category.name}`”)
else:
erreurs.append(f”❌ Catégorie `{nom}` introuvable”)
role = next((r for r in guild.roles if nom.lower() in r.name.lower()), None)
if role:
await role.delete()
supprime.append(f”🎭 Rôle `{role.name}`”)
else:
erreurs.append(f”❌ Rôle `{nom}` introuvable”)
msg = “”
if supprime:
msg += “✅ Supprimé :\n” + “\n”.join(supprime)
if erreurs:
msg += “\n⚠️ Non trouvé :\n” + “\n”.join(erreurs)
await interaction.followup.send(msg)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ➕ /team-add

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“team-add”, description=“Ajoute un membre dans ta team”)
@app_commands.describe(membre=“Le membre à ajouter”, role=“Le rôle de ta team (@mention)”)
async def team_add(interaction: discord.Interaction, membre: discord.Member, role: discord.Role):
auteur = interaction.user
if role not in auteur.roles:
await interaction.response.send_message(f”❌ Tu n’es pas membre de la team `{role.name}`.”, ephemeral=True)
return
if role in membre.roles:
await interaction.response.send_message(f”⚠️ {membre.mention} a déjà le rôle.”, ephemeral=True)
return
await membre.add_roles(role)
try:
embed = discord.Embed(title=“🎉 Bienvenue dans la team !”, description=f”Salut {membre.mention} !\n\nTu as été **accepté(e)** dans la team **{role.name}** sur **{interaction.guild.name}** !\n\nBienvenue parmi nous 🙌”, color=discord.Color.gold())
embed.set_footer(text=f”Ajouté par {auteur.display_name}”)
await membre.send(embed=embed)
mp = “📩 MP envoyé !”
except discord.Forbidden:
mp = “⚠️ MP non envoyé (MPs désactivés)”
await interaction.response.send_message(f”✅ {membre.mention} ajouté à `{role.name}` ! {mp}”)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ➖ /team-remove

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“team-remove”, description=“Retire un membre de ta team”)
@app_commands.describe(membre=“Le membre à retirer”, role=“Le rôle de ta team (@mention)”)
async def team_remove(interaction: discord.Interaction, membre: discord.Member, role: discord.Role):
auteur = interaction.user
if role not in auteur.roles:
await interaction.response.send_message(f”❌ Tu n’es pas membre de la team `{role.name}`.”, ephemeral=True)
return
if role not in membre.roles:
await interaction.response.send_message(f”⚠️ {membre.mention} n’a pas ce rôle.”, ephemeral=True)
return
await membre.remove_roles(role)
await interaction.response.send_message(f”✅ {membre.mention} retiré de `{role.name}` !”)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 📋 /team-list

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“team-list”, description=“Affiche toutes les teams du serveur”)
async def team_list(interaction: discord.Interaction):
guild = interaction.guild

```
# On détecte les vraies teams : catégories qui ont un salon contenant "pour-rejoindre"
teams = []
for category in guild.categories:
    has_rejoindre = any("pour-rejoindre" in c.name.lower() for c in category.channels)
    if has_rejoindre:
        teams.append(category)

if not teams:
    await interaction.response.send_message("❌ Aucune team trouvée.")
    return

embed = discord.Embed(
    title="📋 Teams du serveur",
    description=f"**{len(teams)}** team(s) actives sur **{guild.name}**",
    color=discord.Color.gold()
)

for category in teams:
    # Cherche le rôle avec le même nom
    # Cherche d'abord dans les liaisons manuelles (team-fix)
    role_id = team_roles.get(category.name.lower())
    if role_id:
        role = guild.get_role(role_id)
    else:
        role = next((r for r in guild.roles if category.name.lower() in r.name.lower() or r.name.lower() in category.name.lower()), None)
    nb_membres = len([m for m in guild.members if role in m.roles]) if role else 0
    noms_salons = " • ".join(["`" + c.name + "`" for c in category.channels])
    valeur = f"👥 **{nb_membres}** membre(s)\n"
    valeur += f"💬 {noms_salons}\n"
    valeur += f"🎭 {role.mention}" if role else "🎭 Rôle introuvable"
    embed.add_field(name=category.name, value=valeur, inline=False)

embed.set_footer(text=f"Demandé par {interaction.user.display_name}")
await interaction.response.send_message(embed=embed)
```

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 👤 /team-info

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“team-info”, description=“Affiche les membres d’une team”)
@app_commands.describe(role=“Le rôle de la team (@mention)”)
async def team_info(interaction: discord.Interaction, role: discord.Role):
membres = [m.mention for m in interaction.guild.members if role in m.roles]
embed = discord.Embed(title=f”👥 Team {role.name}”, color=role.color)
embed.add_field(name=f”Membres ({len(membres)})”, value=”\n”.join(membres) if membres else “Aucun membre”, inline=False)
await interaction.response.send_message(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🏓 /ping

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“ping”, description=“Affiche la latence du bot”)
async def ping(interaction: discord.Interaction):
latence = round(bot.latency * 1000)
await interaction.response.send_message(f”🏓 Pong ! Latence : **{latence}ms**”)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ℹ️ /userinfo

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“userinfo”, description=“Affiche les infos d’un membre”)
@app_commands.describe(membre=“Le membre (laisse vide pour toi)”)
async def userinfo(interaction: discord.Interaction, membre: discord.Member = None):
membre = membre or interaction.user
roles = [r.mention for r in membre.roles if r.name != “@everyone”]
embed = discord.Embed(title=f”👤 {membre.display_name}”, color=membre.color)
embed.set_thumbnail(url=membre.display_avatar.url)
embed.add_field(name=“📛 Pseudo”, value=str(membre), inline=True)
embed.add_field(name=“🆔 ID”, value=membre.id, inline=True)
embed.add_field(name=“📅 Arrivé le”, value=membre.joined_at.strftime(”%d/%m/%Y”), inline=True)
embed.add_field(name=“🎂 Compte créé”, value=membre.created_at.strftime(”%d/%m/%Y”), inline=True)
embed.add_field(name=f”🎭 Rôles ({len(roles)})”, value=” “.join(roles) if roles else “Aucun”, inline=False)
await interaction.response.send_message(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🖥️ /serverinfo

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“serverinfo”, description=“Affiche les infos du serveur”)
async def serverinfo(interaction: discord.Interaction):
guild = interaction.guild
embed = discord.Embed(title=f”🖥️ {guild.name}”, color=discord.Color.blurple())
if guild.icon:
embed.set_thumbnail(url=guild.icon.url)
embed.add_field(name=“👑 Propriétaire”, value=guild.owner.mention, inline=True)
embed.add_field(name=“👥 Membres”, value=guild.member_count, inline=True)
embed.add_field(name=“💬 Salons”, value=len(guild.channels), inline=True)
embed.add_field(name=“🎭 Rôles”, value=len(guild.roles), inline=True)
embed.add_field(name=“📅 Créé le”, value=guild.created_at.strftime(”%d/%m/%Y”), inline=True)
await interaction.response.send_message(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🖼️ /avatar

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“avatar”, description=“Affiche l’avatar d’un membre en grand”)
@app_commands.describe(membre=“Le membre (laisse vide pour toi)”)
async def avatar(interaction: discord.Interaction, membre: discord.Member = None):
membre = membre or interaction.user
embed = discord.Embed(title=f”🖼️ Avatar de {membre.display_name}”, color=discord.Color.blurple())
embed.set_image(url=membre.display_avatar.url)
await interaction.response.send_message(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🎱 /8ball

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“8ball”, description=“Pose une question au bot”)
@app_commands.describe(question=“Ta question”)
async def ball8(interaction: discord.Interaction, question: str):
reponses = [
“✅ Oui, absolument !”, “✅ C’est certain !”, “✅ Sans aucun doute !”,
“🤔 Peut-être…”, “🤔 C’est possible.”, “🤔 Je ne suis pas sûr…”,
“❌ Non.”, “❌ Absolument pas !”, “❌ Je ne pense pas.”
]
embed = discord.Embed(title=“🎱 8Ball”, color=discord.Color.dark_purple())
embed.add_field(name=“❓ Question”, value=question, inline=False)
embed.add_field(name=“🔮 Réponse”, value=random.choice(reponses), inline=False)
await interaction.response.send_message(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ✂️ /pierre-feuille-ciseaux

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“pfc”, description=“Pierre, feuille, ciseaux contre le bot”)
@app_commands.describe(choix=“Ton choix”)
@app_commands.choices(choix=[
app_commands.Choice(name=“🪨 Pierre”, value=“pierre”),
app_commands.Choice(name=“📄 Feuille”, value=“feuille”),
app_commands.Choice(name=“✂️ Ciseaux”, value=“ciseaux”),
])
async def pfc(interaction: discord.Interaction, choix: str):
options = [“pierre”, “feuille”, “ciseaux”]
bot_choix = random.choice(options)
emojis = {“pierre”: “🪨”, “feuille”: “📄”, “ciseaux”: “✂️”}
if choix == bot_choix:
resultat = “🤝 Égalité !”
couleur = discord.Color.yellow()
elif (choix == “pierre” and bot_choix == “ciseaux”) or   
(choix == “feuille” and bot_choix == “pierre”) or   
(choix == “ciseaux” and bot_choix == “feuille”):
resultat = “🎉 Tu as gagné !”
couleur = discord.Color.green()
else:
resultat = “😈 Le bot a gagné !”
couleur = discord.Color.red()
embed = discord.Embed(title=“✂️ Pierre Feuille Ciseaux”, color=couleur)
embed.add_field(name=“Ton choix”, value=emojis[choix], inline=True)
embed.add_field(name=“Bot”, value=emojis[bot_choix], inline=True)
embed.add_field(name=“Résultat”, value=resultat, inline=False)
await interaction.response.send_message(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🎲 /dé

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“de”, description=“Lance un dé”)
@app_commands.describe(faces=“Nombre de faces (6 par défaut)”)
async def de(interaction: discord.Interaction, faces: int = 6):
resultat = random.randint(1, faces)
await interaction.response.send_message(f”🎲 Tu as lancé un dé à **{faces}** faces et tu as obtenu : **{resultat}** !”)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🪙 /coinflip

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“coinflip”, description=“Pile ou face”)
async def coinflip(interaction: discord.Interaction):
resultat = random.choice([“🪙 Pile !”, “🪙 Face !”])
await interaction.response.send_message(resultat)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 📊 /poll

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“poll”, description=“Crée un sondage”)
@app_commands.describe(question=“La question du sondage”)
async def poll(interaction: discord.Interaction, question: str):
embed = discord.Embed(title=“📊 Sondage”, description=question, color=discord.Color.blue())
embed.set_footer(text=f”Sondage créé par {interaction.user.display_name}”)
msg = await interaction.channel.send(embed=embed)
await msg.add_reaction(“✅”)
await msg.add_reaction(“❌”)
await interaction.response.send_message(“✅ Sondage créé !”, ephemeral=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 📢 /say

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“say”, description=“Le bot répète ton message”)
@app_commands.describe(message=“Le message à envoyer”)
@app_commands.checks.has_permissions(administrator=True)
async def say(interaction: discord.Interaction, message: str):
await interaction.channel.send(message)
await interaction.response.send_message(“✅ Message envoyé !”, ephemeral=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🎰 /random-membre

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“random-membre”, description=“Choisit un membre aléatoire du serveur”)
async def random_membre(interaction: discord.Interaction):
membres = [m for m in interaction.guild.members if not m.bot]
choix = random.choice(membres)
embed = discord.Embed(title=“🎰 Membre aléatoire !”, description=f”Le bot a choisi : {choix.mention} !”, color=discord.Color.gold())
embed.set_thumbnail(url=choix.display_avatar.url)
await interaction.response.send_message(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🔢 /calcul

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“calcul”, description=“Effectue un calcul simple”)
@app_commands.describe(operation=“Ex: 5 + 3, 10 * 2, 100 / 4”)
async def calcul(interaction: discord.Interaction, operation: str):
try:
resultat = eval(operation, {”**builtins**”: {}})
await interaction.response.send_message(f”🔢 `{operation}` = **{resultat}**”)
except:
await interaction.response.send_message(“❌ Opération invalide.”, ephemeral=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🤫 /mp

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“mp”, description=“Envoie un MP anonyme à un membre via le bot”)
@app_commands.describe(membre=“Le destinataire”, message=“Ton message”)
async def mp(interaction: discord.Interaction, membre: discord.Member, message: str):
try:
await membre.send(f”📩 Tu as reçu un message anonyme sur **{interaction.guild.name}** :\n\n*{message}*”)
await interaction.response.send_message(“✅ MP envoyé anonymement !”, ephemeral=True)
except discord.Forbidden:
await interaction.response.send_message(“❌ Ce membre a ses MPs désactivés.”, ephemeral=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🔧 /team-fix — Lie manuellement un rôle à une team

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“team-fix”, description=“Lie manuellement un rôle à une team”)
@app_commands.describe(
categorie=“Nom exact de la catégorie de la team”,
role=“Le rôle à lier (@mention)”
)
@app_commands.checks.has_permissions(administrator=True)
async def team_fix(interaction: discord.Interaction, categorie: str, role: discord.Role):
team_roles[categorie.lower()] = role.id
await interaction.response.send_message(
f”✅ Lien créé !\n📁 Catégorie : `{categorie}`\n🎭 Rôle : {role.mention}”,
ephemeral=True
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 😂 /blague

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“blague”, description=“Le bot raconte une blague”)
async def blague(interaction: discord.Interaction):
blagues = [
(“Pourquoi les plongeurs plongent-ils toujours en arrière ?”, “Parce que sinon ils tomberaient dans le bateau ! 🤣”),
(“Qu’est-ce qu’un crocodile qui surveille des bagages ?”, “Un gardes-valises ! 😂”),
(“Pourquoi les sorcières ne portent pas de soutien-gorge ?”, “Parce qu’elles n’ont pas de poitrine de sorcière ! 🧙”),
(“Comment appelle-t-on un chat tombé dans un pot de peinture le jour de Noël ?”, “Un chat-peint de Noël ! 🎄”),
(“Qu’est-ce qu’un canif ?”, “Le petit fils du canif… C’est le petit con de ma fille ! 😆”),
(“Pourquoi l’épouvantail a eu un prix ?”, “Parce qu’il était exceptionnel dans son domaine ! 🌾”),
(“C’est l’histoire d’une vague…”, “Elle se brise ! 🌊”),
(“Qu’est-ce qu’un Tic qui tombe d’un arbre ?”, “Un Tac ! 🌳”),
(“Pourquoi les fantômes sont-ils de mauvais menteurs ?”, “Parce qu’on voit à travers eux ! 👻”),
(“Qu’est-ce que l’eau minérale qui court ?”, “Un minéralife ! 💧”),
]
question, reponse = random.choice(blagues)
embed = discord.Embed(title=“😂 Blague du jour”, color=discord.Color.yellow())
embed.add_field(name=“❓”, value=question, inline=False)
embed.add_field(name=“💡”, value=reponse, inline=False)
await interaction.response.send_message(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 💕 /ship

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“ship”, description=“Calcule la compatibilité entre 2 membres”)
@app_commands.describe(membre1=“Premier membre”, membre2=“Deuxième membre”)
async def ship(interaction: discord.Interaction, membre1: discord.Member, membre2: discord.Member):
score = random.randint(0, 100)
if score < 20:
emoji = “💔”
texte = “Aucune chance…”
elif score < 40:
emoji = “😬”
texte = “C’est compliqué…”
elif score < 60:
emoji = “🤔”
texte = “Peut-être ?”
elif score < 80:
emoji = “💛”
texte = “Bonne compatibilité !”
else:
emoji = “💖”
texte = “C’est l’amour fou !”
bar = “█” * (score // 10) + “░” * (10 - score // 10)
embed = discord.Embed(title=f”💕 Ship — {membre1.display_name} & {membre2.display_name}”, color=discord.Color.magenta())
embed.add_field(name=“Compatibilité”, value=f”{emoji} **{score}%**\n`{bar}`\n{texte}”, inline=False)
await interaction.response.send_message(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 😊 /compliment

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“compliment”, description=“Envoie un compliment à quelqu’un”)
@app_commands.describe(membre=“Le membre à complimenter”)
async def compliment(interaction: discord.Interaction, membre: discord.Member):
compliments = [
“Tu es vraiment quelqu’un de génial ! 🌟”,
“Tu illumines ce serveur de ta présence ! ☀️”,
“Tu es une personne incroyable ! 💫”,
“Tout le monde t’apprécie énormément ! 💖”,
“Tu as un talent fou ! 🎯”,
“Tu rends ce serveur meilleur juste en étant là ! 🏆”,
“Tu es une vraie perle rare ! 💎”,
“Ton sens de l’humour est légendaire ! 😂”,
]
embed = discord.Embed(title=“😊 Compliment”, description=f”{membre.mention} — {random.choice(compliments)}”, color=discord.Color.green())
await interaction.response.send_message(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 😈 /insulte

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“insulte”, description=“Insulte rigolote (sans méchanceté)”)
@app_commands.describe(membre=“La cible”)
async def insulte(interaction: discord.Interaction, membre: discord.Member):
insultes = [
“Tu ressembles à un bug qui n’a pas encore été corrigé ! 🐛”,
“T’as le QI d’une plante en pot… et encore, la plante pousse ! 🌵”,
“Tu es la preuve que l’évolution peut parfois faire marche arrière ! 🦆”,
“T’as l’air d’avoir été codé un vendredi à 17h ! 💻”,
“Si l’intelligence était de l’eau, t’aurais même pas de quoi te mouiller les pieds ! 💧”,
“T’es tellement lent que les escargots te doublent ! 🐌”,
“Ta connexion internet est plus rapide que tes neurones ! 📡”,
]
embed = discord.Embed(title=“😈 Insulte rigolote”, description=f”{membre.mention} — {random.choice(insultes)}”, color=discord.Color.red())
embed.set_footer(text=“C’est pour rire hein ! 😄”)
await interaction.response.send_message(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 💭 /citation

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“citation”, description=“Citation inspirante aléatoire”)
async def citation(interaction: discord.Interaction):
citations = [
(“La vie, c’est comme une bicyclette, il faut avancer pour ne pas perdre l’équilibre.”, “Albert Einstein”),
(“Le succès c’est d’aller d’échec en échec sans perdre son enthousiasme.”, “Winston Churchill”),
(“Sois le changement que tu veux voir dans le monde.”, “Gandhi”),
(“L’imagination est plus importante que le savoir.”, “Albert Einstein”),
(“La seule façon de faire du bon travail est d’aimer ce que vous faites.”, “Steve Jobs”),
(“Croyez en vos rêves et ils se réaliseront peut-être. Croyez en vous et ils se réaliseront sûrement.”, “Martin Luther King”),
(“Le courage n’est pas l’absence de peur, mais la capacité de la surmonter.”, “Nelson Mandela”),
]
texte, auteur = random.choice(citations)
embed = discord.Embed(title=“💭 Citation inspirante”, description=f’*”{texte}”*’, color=discord.Color.blurple())
embed.set_footer(text=f”— {auteur}”)
await interaction.response.send_message(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🎯 /deviner

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

parties_deviner = {}

@bot.tree.command(name=“deviner”, description=“Devine un nombre entre 1 et 100”)
@app_commands.describe(nombre=“Ton nombre (laisse vide pour commencer une partie)”)
async def deviner(interaction: discord.Interaction, nombre: int = None):
user_id = interaction.user.id
if nombre is None:
parties_deviner[user_id] = random.randint(1, 100)
await interaction.response.send_message(“🎯 J’ai choisi un nombre entre **1** et **100**. Essaie de le deviner avec `/deviner nombre:XX` !”)
return
if user_id not in parties_deviner:
await interaction.response.send_message(“❌ Lance d’abord une partie avec `/deviner` !”, ephemeral=True)
return
secret = parties_deviner[user_id]
if nombre < secret:
await interaction.response.send_message(f”📈 **{nombre}** c’est trop petit ! Essaie plus grand.”)
elif nombre > secret:
await interaction.response.send_message(f”📉 **{nombre}** c’est trop grand ! Essaie plus petit.”)
else:
del parties_deviner[user_id]
await interaction.response.send_message(f”🎉 Bravo {interaction.user.mention} ! Le nombre était bien **{secret}** !”)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🎭 /vérité-ou-défi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“verite-ou-defi”, description=“Vérité ou défi aléatoire”)
@app_commands.choices(choix=[
app_commands.Choice(name=“🤔 Vérité”, value=“verite”),
app_commands.Choice(name=“😈 Défi”, value=“defi”),
])
@app_commands.describe(choix=“Vérité ou défi ?”)
async def verite_ou_defi(interaction: discord.Interaction, choix: str):
verites = [
“Quel est ton plus grand secret ?”,
“Quelle est la chose la plus embarrassante que tu aies faite ?”,
“Tu as déjà menti à quelqu’un sur ce serveur ?”,
“Quel est ton crush Discord ?”,
“Quelle est ta pire habitude ?”,
“Quel est le message le plus gênant de ton téléphone ?”,
]
defis = [
“Envoie le dernier mème que tu as reçu !”,
“Écris un poème de 2 lignes sur quelqu’un du serveur !”,
“Fais une imitation d’un autre membre !”,
“Envoie ton selfie le plus récent !”,
“Dis 3 choses positives sur quelqu’un du serveur !”,
“Change ton statut Discord pendant 10 minutes !”,
]
if choix == “verite”:
embed = discord.Embed(title=“🤔 Vérité”, description=random.choice(verites), color=discord.Color.blue())
else:
embed = discord.Embed(title=“😈 Défi”, description=random.choice(defis), color=discord.Color.red())
await interaction.response.send_message(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 🏆 /top-membres

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name=“top-membres”, description=“Classement des membres avec le plus de rôles”)
async def top_membres(interaction: discord.Interaction):
membres = [(m, len([r for r in m.roles if r.name != “@everyone”])) for m in interaction.guild.members if not m.bot]
membres.sort(key=lambda x: x[1], reverse=True)
top = membres[:10]
embed = discord.Embed(title=“🏆 Top 10 membres”, color=discord.Color.gold())
medals = [“🥇”, “🥈”, “🥉”] + [“🏅”] * 7
description = “”
for i, (membre, nb_roles) in enumerate(top):
description += f”{medals[i]} **{membre.display_name}** — {nb_roles} rôle(s)\n”
embed.description = description
await interaction.response.send_message(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ❓ /help — Menu d’aide interactif

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HELP_DATA = {
“👥 Team”: {
“team-setup”: (“⭐”, “/team-setup nom:… emoji:…”, “Crée une team complète : catégorie, 4 salons et un rôle. Admin seulement.”, “/team-setup nom:Les Légendes emoji:👑”),
“team-supp”: (“🗑️”, “/team-supp nom:…”, “Supprime une team entière : catégorie, salons et rôle. Admin seulement.”, “/team-supp nom:Les Légendes”),
“team-add”: (“➕”, “/team-add membre:@pseudo role:@role”, “Ajoute un membre dans ta team. Tu dois avoir le rôle. Un MP de bienvenue est envoyé.”, “/team-add membre:@Enzo role:@Les Légendes”),
“team-remove”: (“➖”, “/team-remove membre:@pseudo role:@role”, “Retire un membre de ta team. Tu dois avoir le rôle.”, “/team-remove membre:@Enzo role:@Les Légendes”),
“team-list”: (“📋”, “/team-list”, “Affiche toutes les teams actives avec membres, salons et rôle.”, “/team-list”),
“team-info”: (“👥”, “/team-info role:@role”, “Affiche tous les membres d’une team.”, “/team-info role:@Les Légendes”),
“team-fix”: (“🔧”, “/team-fix categorie:… role:@role”, “Lie manuellement un rôle à une catégorie de team. Admin seulement.”, “/team-fix categorie:La team role:@Nouvel ordre”),
},
“🛠️ Utilitaire”: {
“ping”: (“🏓”, “/ping”, “Affiche la latence du bot en millisecondes.”, “/ping”),
“userinfo”: (“ℹ️”, “/userinfo membre:@pseudo”, “Infos d’un membre : ID, dates, rôles. Laisse vide pour tes infos.”, “/userinfo membre:@Enzo”),
“serverinfo”: (“🖥️”, “/serverinfo”, “Stats du serveur : propriétaire, membres, salons, rôles.”, “/serverinfo”),
“avatar”: (“🖼️”, “/avatar membre:@pseudo”, “Affiche l’avatar d’un membre en grand. Laisse vide pour le tien.”, “/avatar membre:@Enzo”),
“poll”: (“📊”, “/poll question:…”, “Crée un sondage avec réactions ✅ et ❌.”, “/poll question:Vous aimez UraCraft ?”),
“say”: (“📢”, “/say message:…”, “Le bot envoie un message dans le salon. Admin seulement.”, “/say message:Bienvenue !”),
“mp”: (“🤫”, “/mp membre:@pseudo message:…”, “Envoie un MP anonyme à un membre via le bot.”, “/mp membre:@Enzo message:Salut !”),
},
“🎮 Fun”: {
“8ball”: (“🎱”, “/8ball question:…”, “Pose une question, le bot répond Oui / Non / Peut-être.”, “/8ball question:Je vais gagner ?”),
“pfc”: (“✂️”, “/pfc choix:…”, “Pierre Feuille Ciseaux contre le bot.”, “/pfc choix:Pierre”),
“de”: (“🎲”, “/de faces:…”, “Lance un dé. 6 faces par défaut.”, “/de faces:20”),
“coinflip”: (“🪙”, “/coinflip”, “Pile ou face aléatoire.”, “/coinflip”),
“random-membre”: (“🎰”, “/random-membre”, “Choisit un membre aléatoire parmi tous (bots exclus).”, “/random-membre”),
“calcul”: (“🔢”, “/calcul operation:…”, “Effectue un calcul simple (+, -, *, /).”, “/calcul operation:5 * 3 + 2”),
“blague”: (“😂”, “/blague”, “Le bot raconte une blague aléatoire.”, “/blague”),
“ship”: (“💕”, “/ship membre1:@a membre2:@b”, “Calcule la compatibilité entre 2 membres (0-100%).”, “/ship membre1:@Enzo membre2:@Marie”),
“compliment”: (“😊”, “/compliment membre:@pseudo”, “Envoie un compliment aléatoire à quelqu’un.”, “/compliment membre:@Enzo”),
“insulte”: (“😈”, “/insulte membre:@pseudo”, “Insulte rigolote et sans méchanceté. Pour rire !”, “/insulte membre:@Enzo”),
“citation”: (“💭”, “/citation”, “Affiche une citation inspirante aléatoire.”, “/citation”),
“deviner”: (“🎯”, “/deviner | /deviner nombre:XX”, “Devine un nombre entre 1 et 100. Lance d’abord /deviner puis tente ta chance !”, “/deviner | /deviner nombre:42”),
“verite-ou-defi”: (“🎭”, “/verite-ou-defi choix:…”, “Vérité ou défi aléatoire. Choisis entre Vérité ou Défi.”, “/verite-ou-defi choix:Vérité”),
“top-membres”: (“🏆”, “/top-membres”, “Classement des 10 membres avec le plus de rôles.”, “/top-membres”),
},
}

class CmdSelect(discord.ui.Select):
def **init**(self, categorie: str):
self.categorie = categorie
cmds = HELP_DATA[categorie]
options = [
discord.SelectOption(label=f”/{cmd}”, emoji=info[0], value=cmd, description=info[2][:50])
for cmd, info in cmds.items()
]
super().**init**(placeholder=“🔍 Choisis une commande…”, options=options[:25])

```
async def callback(self, interaction: discord.Interaction):
    cmd = self.values[0]
    info = HELP_DATA[self.categorie][cmd]
    embed = discord.Embed(title=f"{info[0]} /{cmd}", color=discord.Color.gold())
    embed.add_field(name="📖 Description", value=info[2], inline=False)
    embed.add_field(name="🔧 Utilisation", value=f"`{info[1]}`", inline=False)
    embed.add_field(name="💡 Exemple", value=f"`{info[3]}`", inline=False)
    embed.add_field(name="📂 Catégorie", value=self.categorie, inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)
```

class CatSelect(discord.ui.Select):
def **init**(self):
options = [
discord.SelectOption(label=cat, value=cat, description=f”{len(cmds)} commandes disponibles”)
for cat, cmds in HELP_DATA.items()
]
super().**init**(placeholder=“📂 Choisis une catégorie…”, options=options)

```
async def callback(self, interaction: discord.Interaction):
    cat = self.values[0]
    cmds = HELP_DATA[cat]
    embed = discord.Embed(title=f"{cat}", description="Sélectionne une commande pour voir les détails :", color=discord.Color.blue())
    for cmd, info in cmds.items():
        embed.add_field(name=f"{info[0]} /{cmd}", value=f"`{info[1]}`", inline=False)
    view = discord.ui.View()
    view.add_item(CmdSelect(cat))
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
```

@bot.tree.command(name=“help”, description=“Affiche toutes les commandes du bot”)
async def help_cmd(interaction: discord.Interaction):
embed = discord.Embed(
title=“📚 Aide — UraBot”,
description=“Sélectionne une **catégorie** dans le menu, puis clique sur une **commande** pour voir les détails !”,
color=discord.Color.gold()
)
for cat, cmds in HELP_DATA.items():
embed.add_field(name=cat, value=f”{len(cmds)} commandes”, inline=True)
embed.set_footer(text=“UraBot — UraCraft”)
view = discord.ui.View()
view.add_item(CatSelect())
await interaction.response.send_message(embed=embed, view=view)

bot.run(TOKEN) 