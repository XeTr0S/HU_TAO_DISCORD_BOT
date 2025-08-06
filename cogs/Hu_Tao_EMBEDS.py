#################################################################################
#                           CLASS - EMBEDEDITOR                                 #
#################################################################################

import discord
import asyncio
from utils.Hu_Tao_PERMSCHECK import check_module_perm
from discord.ext import commands

user_embeds = {}

class EmbedEditor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Création de l'embeds 
    @commands.command(aliases=["create"])
    @check_module_perm("embeds")
    async def create_embed(self, ctx):
        embed = discord.Embed(color=discord.Color.blurple())
        user_embeds[ctx.author.id] = embed
        await ctx.send("✅ Embed initialisé.")

    # Ajout d'un titre 
    @commands.command(aliases=["title"])
    @check_module_perm("embeds")
    async def title_embed(self, ctx, *, title):
        embed = user_embeds.get(ctx.author.id)
        if embed:
            embed.title = title
            await ctx.send("✅ Titre mis à jour.")
        else:
            await ctx.send("❌ Utilise `!create_embed` d'abord.")

    # Ajout d'une description
    @commands.command(aliases=["title2"])
    @check_module_perm("embeds")
    async def desc_embed(self, ctx, *, description):
        embed = user_embeds.get(ctx.author.id)
        if embed:
            embed.description = description
            await ctx.send("✅ Description mise à jour.")
        else:
            await ctx.send("❌ Utilise `!create_embed` d'abord.")

    # Ajout d'un footer
    @commands.command(aliases=["footer"])
    @check_module_perm("embeds")
    async def footer_embed(self, ctx, *, footer_text):
        embed = user_embeds.get(ctx.author.id)
        if embed:
            embed.set_footer(text=footer_text)
            await ctx.send("✅ Footer mis à jour.")
        else:
            await ctx.send("❌ Utilise `!create_embed` d'abord.")

    # Ajout d'une image/gif sur le coin 
    @commands.command(aliases=["corner"])
    @check_module_perm("embeds")
    async def corner_embed(self, ctx, url: str):
        embed = user_embeds.get(ctx.author.id)
        if embed:
            embed.set_thumbnail(url=url)
            await ctx.send("🖼️ Miniature ajoutée.")
        else:
            await ctx.send("❌ Utilise `!create_embed` d'abord.")

    # Ajout de l'image/gif en-dessous de la description
    @commands.command(aliases=["bottom"])
    @check_module_perm("embeds")
    async def bottom_embed(self, ctx, url: str):
        embed = user_embeds.get(ctx.author.id)
        if embed:
            embed.set_image(url=url)
            await ctx.send("🖼️ Image principale ajoutée.")
        else:
            await ctx.send("❌ Utilise `!create_embed` d'abord.")

    # Change la couleur de l'embeds
    @commands.command(aliases=["color"])
    @check_module_perm("embeds")
    async def color_embed(self, ctx, hex_code: str):
        embed = user_embeds.get(ctx.author.id)
        if not embed:
            return await ctx.send("❌ Utilise `!create_embed` d'abord.")

        if hex_code.startswith("#"):
            hex_code = hex_code[1:]

        try:
            color = discord.Color(int(hex_code, 16))
            embed.color = color
            await ctx.send(f"🎨 Couleur mise à jour (`#{hex_code.upper()}`)")
        except ValueError:
            await ctx.send("❌ Code hex invalide. Ex : `#7289DA`")

    # Affiche l'embeds
    @commands.command(aliases=["show"])
    @check_module_perm("embeds")
    async def show_embed(self, ctx):
        embed = user_embeds.get(ctx.author.id)
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Utilise `!create_embed` d'abord.")

    # Envoie l'embeds
    @commands.command(aliases=["send"])
    @check_module_perm("embeds")
    async def send_embed(self, ctx):
        embed = user_embeds.pop(ctx.author.id, None)
        if embed:
            await ctx.send("📤 Embed en cours d'envoie...")
            await asyncio.sleep(1)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Aucun embed à envoyer.")

# Obligatoire pour enregistrer la Cog
async def setup(bot):
    await bot.add_cog(EmbedEditor(bot))