#################################################################################
#                               CLASS - PROFILE                                 #
#################################################################################

import discord
from discord.ext import commands
from discord.ui import View, Select

class ProfileSelector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profil")
    async def profile_command(self, ctx):
        embed = discord.Embed(color=discord.Color.purple())
        embed.title = f"Profil de {ctx.author.name}"
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.add_field(
            name="📝 General",
            value="- Réputation : 0/20\n- Argent : 0$\n- Classement : 1",
            inline=False
        )
        embed.add_field(
            name="⚡ Statistique",
            value="- Force : 1.0\n- PV : 20.0\n- Défense : 20.0\n- Vitesse : 10\n- Dextérité : 20\n- Précision : 0",
            inline=False
        )
        embed.add_field(
            name="🪪 Personnage",
            value="Aucun personnage RP pour l'instant.",
            inline=False
        )

        await ctx.send(embed=embed, view=ProfileView(ctx.author))


class ProfileView(View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user
        self.add_item(ProfileSelect(user))

class ProfileSelect(Select):
    def __init__(self, user):
        self.user = user
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

        embed = discord.Embed(color=discord.Color.purple())

        if self.values[0] == "1":
            embed.title = f"Profil de {self.user.name}"
            embed.set_thumbnail(url=self.user.display_avatar.url)
            embed.add_field(name="📝 General", value="- Réputation : 0/20\n- Argent : 0$\n- Classement : 1", inline=False)
            embed.add_field(name="⚡ Statistique", value="- Force : 1.0\n- PV : 20.0\n- Défense : 20.0\n- Vitesse : 10\n- Dextérité : 20\n- Précision : 0", inline=False)
            embed.add_field(name="🪪 Personnage", value="Aucun personnage RP pour l'instant.", inline=False)

        elif self.values[0] == "2":
            embed.title = f"Inventaire de {self.user.name}"
            embed.description = "💼 Aucun objet dans l'inventaire pour l'instant."

        elif self.values[0] == "3":
            embed.title = f"Techniques & Capacités de {self.user.name}"
            embed.description = "🌑 Aucune technique ou capacité spéciale enregistrée."

        await interaction.response.edit_message(embed=embed, view=self.view)

async def setup(bot):
    await bot.add_cog(ProfileSelector(bot))