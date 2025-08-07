#################################################################################
#                             CLASS - PROFILE                                   #
#################################################################################

import os
import json
import discord
from discord.ext import commands
from discord.ui import View, Select
from cogs.Hu_Tao_STATS import STATS  # pour accéder à load_user_data et la liste des stats

class ProfileSelector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_profile_embed(self, user):
        embed = discord.Embed(color=discord.Color.purple())
        embed.title = f"Profil de {user.name}"
        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(name="📝 General", value="- Réputation : 0\n- Argent : 0$\n- Classement :", inline=False)
        embed.add_field(name="🛡️​ Rank", value="- Rank F", inline=False)

        # Charger les stats du joueur depuis le fichier JSON
        stats_folder = os.path.join("datas", "stats", f"{user.id}.json")
        if os.path.exists(stats_folder):
            with open(stats_folder, "r", encoding="utf-8") as f:
                stats_data = json.load(f)
            stat_text = "\n".join([f"- {stat.title()} : {stats_data['stats'].get(stat, 0)}" for stat in STATS])
        else:
            stat_text = "Aucune statistique enregistrée."

        embed.add_field(name="⚡ Statistique", value=stat_text, inline=False)

        # 🪪 Personnage
        ocs_path = os.path.join("datas", "ocs", f"{user.id}.json")
        if os.path.exists(ocs_path):
            with open(ocs_path, "r", encoding="utf-8") as file:
                ocs = json.load(file)

            main_oc = ocs.get("_main")
            all_ocs = [k for k in ocs.keys() if not k.startswith("_")]
            featured = all_ocs[:3]  # Les 3 premiers OC par défaut

            text = ""
            if main_oc:
                text += f"⭐ **Principal :** {main_oc}\n"
            if featured:
                text += f"🎭 **À l'affiche :** {', '.join(featured)}\n"

            if not text:
                text = "Aucun personnage RP pour l'instant."
        else:
            text = "Aucun personnage RP pour l'instant."

        embed.add_field(name="🪪 Personnage", value=text, inline=False)
        return embed

    @commands.command(name="profil")
    async def profile_command(self, ctx, member: discord.Member = None):
        member = member or ctx.author  # Si rien n'est précisé → l'auteur
        embed = self.get_profile_embed(member)
        await ctx.send(embed=embed, view=ProfileView(member, self))

class ProfileView(View):
    def __init__(self, user, profile_cog):
        super().__init__(timeout=None)
        self.user = user
        self.add_item(ProfileSelect(user, profile_cog))

class ProfileSelect(Select):
    def __init__(self, user, profile_cog):
        self.user = user
        self.profile_cog = profile_cog
        options = [
            discord.SelectOption(label="📝 Profil", description="Informations générales & statistiques", value="1"),
            discord.SelectOption(label="💼 Inventaire", description="Inventaire de vos objets", value="2"),
            discord.SelectOption(label="🌑 Technique/Capacité", description="Techniques et capacités spéciales", value="3"),
        ]
        super().__init__(placeholder="Choisissez une vue de profil...", options=options, custom_id="profile_select")

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Ce menu ne t'appartient pas.", ephemeral=True)
            return

        if self.values[0] == "1":
            embed = self.profile_cog.get_profile_embed(self.user)
        elif self.values[0] == "2":
            embed = discord.Embed(title=f"Inventaire de {self.user.name}", description="💼 Aucun objet dans l'inventaire pour l'instant.", color=discord.Color.purple())
        elif self.values[0] == "3":
            embed = discord.Embed(title=f"Techniques & Capacités de {self.user.name}", description="🌑 Aucune technique ou capacité spéciale enregistrée.", color=discord.Color.purple())

        await interaction.response.edit_message(embed=embed, view=self.view)

async def setup(bot):
    await bot.add_cog(ProfileSelector(bot))