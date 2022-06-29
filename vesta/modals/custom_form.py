import re

from discord import app_commands
import discord.ui
from sqlalchemy import select

from .. import session, partabot_client
from ..tables import User, CustomCommand

url_regex = r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
http_regex = r'https?:\/\/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'

class CustomSlashForm(discord.ui.Modal, title="Création d'une commande custom"):
    command_title = discord.ui.TextInput(
        label="Titre du message",
        style=discord.TextStyle.short,
        max_length=255
    )
    command_content = discord.ui.TextInput(
        label="Contenu du message",
        style=discord.TextStyle.long,
    )
    command_url = discord.ui.TextInput(
        label="Lien",
        style=discord.TextStyle.short,
        required=False,
        max_length=511
    )
    command_image = discord.ui.TextInput(
        label="Image",
        style=discord.TextStyle.short,
        required=False,
        max_length=511
    )
    command_colour = discord.ui.TextInput(
        label="Couleur de l'embed",
        style=discord.TextStyle.short,
        placeholder="fdfd58",
        required=False,
        max_length=6,
        min_length=6
    )

    def __init__(self, keyword):
        super().__init__()
        self.keyword = keyword


    async def on_submit(self, interaction: discord.Interaction):
        command_url = self.command_url.value
        if command_url and not re.match(http_regex, command_url):
            if re.match(url_regex, command_url):
                command_url = 'https://' + command_url
            else:
                return await interaction.response.send_message(
                    content="Le lien n'est pas valide",
                    ephemeral=True,
                )
        image_url = self.command_image.value
        if image_url and not re.match(http_regex, image_url):
            if re.match(url_regex, image_url):
                image_url = 'https://' + image_url
            else:
                return await interaction.response.send_message(
                    content="Le lien de votre image n'est pas valide",
                    ephemeral=True,
                )
        r = select(User).where(User.id == interaction.user.id)
        author = session.scalar(r)
        if not author:
            author = User(
                id=interaction.user.id,
                name=interaction.user.display_name,
                avatar_url=interaction.user.display_avatar.url
            )
            session.add(author)
        r = select(CustomCommand).where(CustomCommand.guild_id == interaction.guild_id)
        r = r.where(CustomCommand.keyword == self.keyword)
        if session.scalar(r):
            return await interaction.response.send_message("La commande existe déjà", ephemeral=True)
        custom_command = CustomCommand(
            guild_id=interaction.guild_id,
            keyword=self.keyword,
            title=self.command_title.value,
            content=self.command_content.value,
            source_url=command_url,
            image_url=image_url,
            colour=int(self.command_colour.value, 16) if self.command_colour.value else None,
            author=author
        )
        session.add(custom_command)
        session.commit()
        await interaction.response.send_message("La commande à bien été créée !", ephemeral=True)

        @app_commands.guild_only()
        async def command(interaction: discord.Interaction):
            await interaction.response.send_message(embed=custom_command.embed())

        custom = app_commands.Command(name=self.keyword, description=self.command_title.value, callback=command)

        partabot_client.tree.add_command(custom, guild=interaction.guild)
        await partabot_client.tree.sync(guild=interaction.guild)

class CustomMenuForm(discord.ui.Modal, title="Création d'une commande custom"):
    command_keyword = discord.ui.TextInput(
        label="Keyword de la commande",
        max_length=32
    )
    command_title = discord.ui.TextInput(
        label="Titre du message",
        style=discord.TextStyle.short,
        max_length=255
    )
    command_url = discord.ui.TextInput(
        label="Lien",
        style=discord.TextStyle.short,
        required=False,
        max_length=511
    )
    command_image = discord.ui.TextInput(
        label="Image",
        style=discord.TextStyle.short,
        required=False,
        max_length=511
    )
    command_colour = discord.ui.TextInput(
        label="Couleur de l'embed",
        style=discord.TextStyle.short,
        placeholder="fdfd58",
        required=False,
        max_length=6,
        min_length=6
    )

    def __init__(self, content, author):
        super().__init__()
        self.content = content
        self.author = author


    async def on_submit(self, interaction: discord.Interaction):
        command_url = self.command_url.value
        if command_url and not re.match(http_regex, command_url):
            if re.match(url_regex, command_url):
                command_url = 'https://' + command_url
            else:
                return await interaction.response.send_message(
                    content="Le lien n'est pas valide",
                    ephemeral=True,
                )
        image_url = self.command_image.value
        if image_url and not re.match(http_regex, image_url):
            if re.match(url_regex, image_url):
                image_url = 'https://' + image_url
            else:
                return await interaction.response.send_message(
                    content="Le lien de votre image n'est pas valide",
                    ephemeral=True,
                )
        r = select(User).where(User.id == self.author.id)
        author = session.scalar(r)
        if not author:
            author = User(
                id=self.author.id,
                name=self.author.display_name,
                avatar_url=self.author.display_avatar.url
            )
            session.add(author)
        r = select(CustomCommand).where(CustomCommand.guild_id == interaction.guild_id)
        r = r.where(CustomCommand.keyword == self.command_keyword.value)
        if session.scalar(r):
            return await interaction.response.send_message("La commande existe déjà", ephemeral=True)
        custom_command = CustomCommand(
            guild_id=interaction.guild_id,
            keyword=self.command_keyword.value,
            title=self.command_title.value,
            content=self.content,
            source_url=command_url,
            image_url=image_url,
            colour=int(self.command_colour.value, 16) if self.command_colour.value else None,
            author=author,
        )
        session.add(custom_command)
        session.commit()
        await interaction.response.send_message("La commande à bien été créée !", ephemeral=True)

        @app_commands.guild_only()
        async def command(interaction: discord.Interaction):
            await interaction.response.send_message(embed=custom_command.embed())

        custom = app_commands.Command(name=self.command_keyword.value, description=self.command_title.value, callback=command)

        partabot_client.tree.add_command(custom, guild=interaction.guild)
        await partabot_client.tree.sync(guild=interaction.guild)