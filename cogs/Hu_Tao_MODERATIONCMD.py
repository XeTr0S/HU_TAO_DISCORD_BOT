#################################################################################
#                           CLASS - MODERATION                                  #
#################################################################################

import os
import json
import discord
from discord.ext import commands
from datetime import datetime
from utils.Hu_Tao_PERMSCHECK import check_module_perm

REPORT_CHANNEL_ID = 1402342852393959545  # ← remplace par l’ID du salon où tu veux envoyer les reports

class ModsPermissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logs_path = os.path.join("logs_report", "Hu_Tao_logs_report.json")

    # Commandes de setpermissions
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setperm(self, ctx, module: str, *, roles_csv: str):
        roles = [role.strip().strip('"') for role in roles_csv.split(",")]

        try:
            with open(os.path.join("config", "Hu_Tao_permissions.json"), "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        data[module] = roles

        with open(os.path.join("config", "Hu_Tao_permissions.json"), "w") as f:
            json.dump(data, f, indent=4)

        await ctx.send(f"✅ Permissions mises à jour pour le module `{module}` : {', '.join(roles)}")

    # commande de report
    @commands.command(name="report")
    async def report(self, ctx, *, raison: str):

        # Ignorer si ce n’est pas un MP
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.message.delete()
            try:
                await ctx.author.send("❌ Merci de m’envoyer le report en MP pour garantir la confidentialité.")
            except Exception as e:
                print(f"[ERREUR] Impossible de DM {ctx.author}: {e}")
            return

        user = ctx.author
        timestamp = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")

        # Générer l'embed
        embed = discord.Embed(
            title=f"{user.name} ({user.id})",
            description=raison,
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Report reçu le {timestamp}")

        # Envoi dans le salon de modération
        report_channel_id = REPORT_CHANNEL_ID  # Remplace par ton ID de salon
        channel = self.bot.get_channel(report_channel_id)
        if not channel:
            await user.send("❌ Le salon de modération n’a pas été trouvé. Contacte un admin.")
            return

        try:
            message = await channel.send(embed=embed)
        except Exception as e:
            await user.send("❌ Une erreur est survenue lors de l’envoi du report.")
            print(f"[ERREUR] Envoi embed échoué : {e}")
            return

        # Log dans le fichier JSON
        report_data = {
            "user_id": user.id,
            "raison": raison,
            "timestamp": timestamp,
            "message_id": message.id,
            "status": "En attente"
        }

        try:
            if os.path.exists(self.logs_path):
                with open(self.logs_path, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            else:
                logs = {}

            logs[str(user.id)] = report_data

            with open(self.logs_path, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"[ERREUR] Sauvegarde JSON échouée : {e}")
            await user.send("⚠️ Le report a été envoyé mais n’a pas pu être enregistré.")

        await user.send("✅ Ton report a bien été transmis aux modérateurs.")
    
    # Commande Reply report
    @commands.command(name="replyreport", aliases=["reply"])
    @check_module_perm("mods")
    async def replyreport(self, ctx, user_id: int, status: str, *, raison: str):
        timestamp = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")

        # Couleur en fonction du statut
        status_colors = {
            "En attente": discord.Color.gold(),
            "En cours": discord.Color.blue(),
            "Résolu": discord.Color.green(),
            "Anomalie": discord.Color.red()
        }
        color = status_colors.get(status.capitalize(), discord.Color.light_grey())

        # Vérifier et charger les logs
        if not os.path.exists(self.logs_path):
            await ctx.send("❌ Aucun fichier de logs trouvé.")
            return

        try:
            with open(self.logs_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception as e:
            await ctx.send("❌ Erreur de lecture des logs.")
            print(f"[ERREUR] Lecture logs JSON : {e}")
            return

        if str(user_id) not in logs:
            await ctx.send("❌ Aucun report trouvé pour cet ID.")
            return

        try:
            user = await self.bot.fetch_user(user_id)
        except Exception as e:
            await ctx.send("❌ Utilisateur introuvable.")
            print(f"[ERREUR] fetch_user : {e}")
            return

        # Créer l'embed de réponse
        embed = discord.Embed(
            title=f"Merci de ton signalement ({user.name}) !",
            description=raison,
            color=color
        )

        # Ligne compacte : modérateur + statut
        embed.add_field(
            name="🛠️ Répondu par :",
            value=f"{ctx.author.name}    |    Statut : {status.capitalize()}",
            inline=False
        )

        embed.set_footer(text=f"Répondu le {timestamp}")
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        try:
            await user.send(embed=embed)
            await ctx.send(f"📨 Réponse envoyée à {user.name}.")
        except Exception as e:
            await ctx.send("❌ Impossible d’envoyer un MP à l’utilisateur.")
            print(f"[ERREUR] DM failed : {e}")
            return

        # Mise à jour des logs
        logs[str(user_id)]["status"] = status
        logs[str(user_id)]["moderator"] = ctx.author.name
        logs[str(user_id)]["reply_timestamp"] = timestamp
        logs[str(user_id)]["reply_reason"] = raison

        try:
            with open(self.logs_path, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=4, ensure_ascii=False)
            print("[DEBUG] Logs mis à jour après reply.")
        except Exception as e:
            await ctx.send("⚠️ La réponse a été envoyée mais n’a pas pu être enregistrée.")
            print(f"[ERREUR] Écriture logs JSON : {e}")

# Chargement automatique de la cog
async def setup(bot):
    await bot.add_cog(ModsPermissions(bot))