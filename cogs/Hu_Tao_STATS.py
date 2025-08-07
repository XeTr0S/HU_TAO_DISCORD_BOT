#################################################################################
#                             CLASS - STATISTIQUES                              #
#################################################################################

import json
import os
import random
import asyncio
import discord
from discord.ext import commands

# Répartition des points requis pour chaque palier (ex: palier 2 → 5 pts requis pour y accéder)
PALIER_COST = {
    0: 0,
    1: 5, 
    2: 12, 
    3: 19, 
    4: 32, 
    5: 60,
    6: 105, 
    7: 155, 
    8: 210, 
    9: 280, 
    10: 360
}

STATS = ["force", "magie", "pv", "defense", "vitesse", "dexterite", "precision", "intelligence", "charisme", "chance"]

class Statistiques(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.folder = "datas/stats"
        os.makedirs(self.folder, exist_ok=True)

    def get_user_path(self, user_id):
        return os.path.join(self.folder, f"{user_id}.json")

    def load_user_data(self, user_id):
        path = self.get_user_path(user_id)

        if not os.path.exists(path):
            data = {
                "points_disponibles": 0,
                "stats": {stat: 0 for stat in STATS},
                "progression": {stat: 0 for stat in STATS}
            }
            self.save_user_data(user_id, data)
        else:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 🔁 S'assurer que la clé "progression" est présente
            if "progression" not in data:
                data["progression"] = {stat: 0 for stat in STATS}

        return data

    def save_user_data(self, user_id, data):
        with open(self.get_user_path(user_id), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # Affichage des stats
    @commands.command()
    async def stats(self, ctx):
        data = self.load_user_data(ctx.author.id)
        stats = data["stats"]
        progressions = data["progression"]
        points = data["points_disponibles"]

        def barre_niveau(niveau):
            max_niveau = 10
            return f"[{'■'*niveau}{'□'*(max_niveau-niveau)}]"

        def points_requis(niveau, progress):
            if niveau >= 10:
                return "✅ Max atteint"
            restant = PALIER_COST[niveau + 1] - PALIER_COST[niveau] - progress
            return f"{restant} pts restants"

        embed = discord.Embed(
            title=f"📊 Statistiques de {ctx.author.display_name}",
            description=f"🎯 Points disponibles : **{points}**",
            color=discord.Color.blue()
        )

        for stat in STATS:
            lvl = stats[stat]
            prog = progressions.get(stat, 0)
            embed.add_field(
                name=f"**{stat.title()}**",
                value=f"{barre_niveau(lvl)} ({lvl})\n🡆 Prochain palier : {points_requis(lvl, prog)}",
                inline=False
            )

        await ctx.send(embed=embed)

    # Commande pour se train
    @commands.command()
    @commands.cooldown(3, 86400, commands.BucketType.user)
    async def train(self, ctx):
        data = self.load_user_data(ctx.author.id)

        if random.random() <= 0.70:
            data["points_disponibles"] += 1
            self.save_user_data(ctx.author.id, data)
            await ctx.send(f"✅ Entraînement réussi ! Tu gagnes **1** point d'attribut. Tu peux l'attribuer avec `!skilladd`.")
        else:
            await ctx.send(f"❌ L'entraînement a échoué. Réessaie demain !")

    @train.error
    async def train_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = int(error.retry_after)
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            await ctx.send(
                f"⏳ Tu as déjà utilisé cette commande 3 fois aujourd'hui.\n"
                f"🕒 Réessaie dans **{hours}h {minutes}min**."
            )

    # Ajouter un point d'attribut dans une stats
    @commands.command()
    async def skilladd(self, ctx, stat: str, points: int = 1):
        stat = stat.lower()
        if stat not in STATS:
            await ctx.send(f"❌ Statistique invalide. Stats valides : {', '.join(STATS)}")
            return

        data = self.load_user_data(ctx.author.id)
        lvl = data["stats"][stat]
        prog = data["progression"][stat]
        dispo = data["points_disponibles"]

        if lvl >= 10:
            await ctx.send("🚫 Stat déjà au niveau maximum.")
            return

        if points <= 0:
            await ctx.send("❌ Tu dois utiliser au moins 1 point.")
            return

        if dispo < points:
            await ctx.send(f"❌ Tu n’as que **{dispo}** points disponibles.")
            return

        cost = PALIER_COST[lvl + 1] - PALIER_COST[lvl]
        total_progress = prog + points
        new_level = lvl
        used = points

        # Monter de niveau tant que possible
        while total_progress >= cost and new_level < 10:
            total_progress -= cost
            new_level += 1
            if new_level < 10:
                cost = PALIER_COST[new_level + 1] - PALIER_COST[new_level]

        # Mise à jour des données
        data["points_disponibles"] -= used
        data["stats"][stat] = new_level
        data["progression"][stat] = total_progress
        self.save_user_data(ctx.author.id, data)

        await ctx.send(
            f"📈 **{stat.title()}** → Palier **{new_level}**\n"
            f"🔻 Points utilisés : {used}\n"
            f"🡆 Progrès vers le prochain palier : {total_progress}/{PALIER_COST[new_level + 1] - PALIER_COST[new_level]}" if new_level < 10 else "✅ Max atteint"
        )

    # Reset des points d'attributs/stats
    @commands.command()
    async def resetstats(self, ctx):
        await ctx.send("❗ Es-tu sûr de vouloir **réinitialiser toutes tes stats** ? (oui/non)")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["oui", "non"]

        try:
            response = await self.bot.wait_for("message", check=check, timeout=20)
            if response.content.lower() == "oui":
                data = {"points_disponibles": 0, "stats": {stat: 0 for stat in STATS}}
                self.save_user_data(ctx.author.id, data)
                await ctx.send("🔄 Tes statistiques ont été **réinitialisées**.")
            else:
                await ctx.send("❌ Réinitialisation annulée.")
        except asyncio.TimeoutError:
            await ctx.send("⏰ Temps écoulé. Réinitialisation annulée.")

async def setup(bot):
    await bot.add_cog(Statistiques(bot))