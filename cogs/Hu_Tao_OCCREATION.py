#################################################################################
#                             CLASS - OC CREATION                               #
#################################################################################

import discord
import json
import os
from utils.Hu_Tao_PERMSCHECK import check_module_perm
from discord.ext import commands

OCS_FOLDER = "datas/ocs"

class OCCREATION(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        os.makedirs(OCS_FOLDER, exist_ok=True)

    def get_user_ocs_path(self, user_id):
        return os.path.join(OCS_FOLDER, f"{user_id}.json")

    def load_ocs(self, user_id):
        path = self.get_user_ocs_path(user_id)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}

    def save_ocs(self, user_id, data):
        with open(self.get_user_ocs_path(user_id), "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    # Création d’un OC
    @commands.command(name="occreate")
    @check_module_perm("occreation")
    async def occreate(self, ctx, name: str, prefix: str):
        """
        !occreate "Nom Complet" Prefix:
        Ajoute une image en pièce jointe pour l'avatar.
        """
        ocs = self.load_ocs(ctx.author.id)

        if not ctx.message.attachments:
            await ctx.send("❌ Merci d’attacher une image comme avatar.")
            return

        image = ctx.message.attachments[0]
        if not image.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            await ctx.send("❌ Format d’image non supporté.")
            return

        # 🔍 Cherche le salon d’upload CDN
        upload_channel = discord.utils.get(ctx.guild.text_channels, name="cdn-uploads")
        if not upload_channel:
            await ctx.send("❌ Le salon `cdn-uploads` est introuvable.")
            return

        # 🖼️ Upload de l’image dans le salon CDN
        upload_msg = await upload_channel.send(file=await image.to_file())
        cdn_url = upload_msg.attachments[0].url

        # 📝 Enregistrement
        ocs[name] = {
            "avatar": cdn_url,
            "avatar_msg_id": upload_msg.id,
            "prefix": prefix.strip()
        }
        self.save_ocs(ctx.author.id, ocs)

        await ctx.send(f"✅ OC **{name}** créé avec succès !")

    # Supprimer un OC
    @commands.command(name="ocremove")
    @check_module_perm("occreation")
    async def ocremove(self, ctx, name: str):
        """
        !ocremove "Nom_OC"
        Supprime un OC et supprime aussi l’image du CDN si elle existe.
        """
        ocs = self.load_ocs(ctx.author.id)

        if name not in ocs:
            await ctx.send("❌ Aucun OC trouvé avec ce nom.")
            return

        # 🔍 Chercher le salon d’upload
        upload_channel = discord.utils.get(ctx.guild.text_channels, name="cdn-uploads")
        if not upload_channel:
            await ctx.send("❌ Le salon `cdn-uploads` est introuvable. OC supprimé localement seulement.")
            del ocs[name]
            self.save_ocs(ctx.author.id, ocs)
            return

        try:
            # 🗑️ Supprimer l’image d’avatar du CDN si ID stocké
            avatar_msg_id = ocs[name].get("avatar_msg_id")
            if avatar_msg_id:
                try:
                    msg = await upload_channel.fetch_message(avatar_msg_id)
                    await msg.delete()
                except discord.NotFound:
                    pass  # Déjà supprimé ou inexistant

            # 🧽 Supprimer l'OC localement
            del ocs[name]
            self.save_ocs(ctx.author.id, ocs)

            await ctx.send(f"🗑️ OC **{name}** et son image ont bien été supprimés.")
        except Exception as e:
            await ctx.send("⚠️ OC supprimé mais une erreur est survenue pendant la suppression de l'image.")
            print(f"[OC Remove Error] {e}")

    # Lister les OC
    @commands.command(name="oclist")
    @check_module_perm("occreation")
    async def oclist(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        ocs = self.load_ocs(member.id)
        if not ocs:
            await ctx.send("⚠️ Aucun OC trouvé pour cet utilisateur.")
            return

        embed = discord.Embed(
            title=f"OC de {member.display_name}",
            color=discord.Color.dark_blue()
        )

        upload_channel = discord.utils.get(ctx.guild.text_channels, name="cdn-uploads")

        for name, data in ocs.items():
            if name.startswith("_"):  # ignore les clés internes comme _main
                continue

            prefix = data.get("prefix", "❓")
            avatar = data.get("avatar", "Non défini")
            msg_count = data.get("messages_sent", 0)
            msg_id = data.get("avatar_msg_id")

            created_str = "❓"
            if upload_channel and msg_id:
                try:
                    msg = await upload_channel.fetch_message(msg_id)
                    created_str = discord.utils.format_dt(msg.created_at, style="F")  # date complète
                except discord.NotFound:
                    created_str = "🔸 Supprimé"

            embed.add_field(
                name=f"📌 {name}",
                value=(
                    f"> Préfixe : `{prefix}`\n"
                    f"> Avatar : [Lien]({avatar})\n"
                    f"> Messages envoyés : `{msg_count}`\n"
                    f"> Créé le : {created_str}"
                ),
                inline=False
            )

        await ctx.send(embed=embed)

    # Modification de l'avatar OC
    @commands.command(name="ocavataredit")
    @check_module_perm("occreation")
    async def ocavataredit(self, ctx, name: str):
        """
        !ocavataredit "Nom_OC"
        Joindre une nouvelle image en pièce jointe pour mettre à jour l'avatar.
        """
        ocs = self.load_ocs(ctx.author.id)

        if name not in ocs:
            await ctx.send("❌ Aucun OC trouvé avec ce nom.")
            return

        if not ctx.message.attachments:
            await ctx.send("❌ Merci d’attacher une image.")
            return

        image = ctx.message.attachments[0]
        if not image.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            await ctx.send("❌ Format d’image non supporté.")
            return

        upload_channel = discord.utils.get(ctx.guild.text_channels, name="cdn-uploads")
        if not upload_channel:
            await ctx.send("❌ Le salon `cdn-uploads` est introuvable.")
            return

        try:
            # 🗑️ Supprimer l’ancien message CDN si stocké
            old_msg_id = ocs[name].get("avatar_msg_id")
            if old_msg_id:
                try:
                    old_msg = await upload_channel.fetch_message(old_msg_id)
                    await old_msg.delete()
                except discord.NotFound:
                    pass  # Message déjà supprimé ou introuvable

            # 📤 Upload image et stocke le message ID
            upload_msg = await upload_channel.send(file=await image.to_file())
            cdn_url = upload_msg.attachments[0].url
            cdn_msg_id = upload_msg.id

            # 💾 Mettre à jour les données
            ocs[name]["avatar"] = cdn_url
            ocs[name]["avatar_msg_id"] = cdn_msg_id
            self.save_ocs(ctx.author.id, ocs)

            await ctx.send(f"✅ Avatar de **{name}** mis à jour avec succès.")

        except Exception as e:
            await ctx.send("❌ Une erreur est survenue lors de l'upload.")
            print(f"[OC Avatar Edit Error] {e}")

    # Auto-proxy (comme Tupperbox)
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        ocs = self.load_ocs(message.author.id)

        for name, data in ocs.items():
            prefix = data["prefix"]
            lowered_content = message.content.lower()
            lowered_prefix = prefix.lower()

            if lowered_content.startswith(lowered_prefix):

                # Récupère le contenu brut, à partir de la fin du préfixe
                raw_content = message.content[len(prefix):]

                # Supprime les espaces, tabulations et sauts de ligne au début
                content = raw_content.lstrip(" \t\n\r")

                try:
                    avatar_path = data["avatar"]
                    is_local_avatar = avatar_path.startswith("datas/ocs_avatars")

                    # Préparation des fichiers (message + avatar)
                    files = []
                    for attachment in message.attachments:
                        file = await attachment.to_file()
                        files.append(file)

                    if is_local_avatar:
                        # On fixe le nom du fichier à "avatar.png" pour éviter les erreurs de chemin Windows
                        avatar_file = discord.File(avatar_path, filename="avatar.png")
                        files.append(avatar_file)
                        avatar_url = "attachment://avatar.png"
                    else:
                        avatar_url = avatar_path

                    # Envoi via webhook
                    webhook = await message.channel.create_webhook(name=name)
                    await webhook.send(
                        content,
                        username=name,
                        avatar_url=avatar_url,
                        files=files
                    )

                    # ➕ Incrémentation du compteur de messages
                    ocs = self.load_ocs(message.author.id)
                    if name in ocs:
                        ocs[name]["messages_sent"] = ocs[name].get("messages_sent", 0) + 1
                        self.save_ocs(message.author.id, ocs)

                    await webhook.delete()
                    await message.delete()

                except Exception as e:
                    print(f"Erreur Webhook OC: {e}")

    # Définir le main OC
    @commands.command(name="mainoc")
    @check_module_perm("occreation")
    async def mainoc(self, ctx, *, name: str):
        """
        !mainoc Nom_OC
        Définit le personnage principal de votre profil.
        """

        # Match insensible à la casse
        ocs = self.load_ocs(ctx.author.id)
        matched_name = next((n for n in ocs if n.lower() == name.lower()), None)
        if not matched_name:
            await ctx.send("❌ Aucun OC trouvé avec ce nom.")
            return

        ocs["_main"] = name
        self.save_ocs(ctx.author.id, ocs)
        await ctx.send(f"🌟 **{name}** est désormais votre personnage principal.")

    # Retire le main OC
    @commands.command(name="mainocremove")
    @check_module_perm("occreation")
    async def mainocremove(self, ctx):
        """
        !mainocremove
        Retire le personnage principal de votre profil.
        """
        ocs = self.load_ocs(ctx.author.id)

        if "_main" not in ocs:
            await ctx.send("❌ Aucun personnage principal n'est défini.")
            return

        removed = ocs.pop("_main")
        self.save_ocs(ctx.author.id, ocs)
        await ctx.send(f"🔹 Le personnage principal **{removed}** a été retiré de votre profil.")

async def setup(bot):
    await bot.add_cog(OCCREATION(bot))