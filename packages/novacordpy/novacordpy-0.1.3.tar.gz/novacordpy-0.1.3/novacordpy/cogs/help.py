from __future__ import annotations

import inspect
import random
from copy import deepcopy

from .. import emb
from ..bot import Bot, Cog
from ..components import View
from ..enums import HelpStyle
from ..i18n import I18N
from ..internal import fill_custom_variables, replace_embed_values, tr
from ..internal.dc import PYCORD, discord, slash_command
from ..logs import log


def get_emoji(cog: Cog) -> str:
    """Wählt ein Emoji für einen Cog aus (entweder festgelegt oder zufällig)."""
    if hasattr(cog, "emoji") and cog.emoji:
        return cog.emoji
    return random.choice(["🔰", "👻", "🍪", "👥", "🦕", "🐧", "✨", "🍔", "⚡", "🛠️"])


def get_group(cog: Cog, cog_name: str, locale: str) -> tuple[str | None, str]:
    """Liefert die Gruppe und lokalisierten Namen eines Cogs zurück."""
    group = getattr(cog, "group", None)
    name = group if group else cog_name
    localized_name = None

    if hasattr(cog, "name_localizations"):
        localized_name = cog.name_localizations.get(locale, cog_name)

    try:
        localized_name = I18N.cmd_localizations[locale]["cogs"][name]["name"]
    except (KeyError, AttributeError):
        pass

    return group, localized_name or name


def replace_placeholders(s: str, **kwargs: str):
    for key, value in kwargs.items():
        if value:
            s = s.replace(f"{{{key}}}", value)
    return s


def get_cmd_desc(command, locale: str):
    """Liefert die lokalisierte Beschreibung eines Befehls zurück."""
    if command.description_localizations is not discord.MISSING:
        return command.description_localizations.get(locale, command.description)
    return command.description


def get_cog_desc(cog, locale: str) -> str | None:
    if hasattr(cog, "description_localizations"):
        return cog.description_localizations.get(locale, cog.description)
    return getattr(cog, "description", None)


def get_perm_parent(cmd: discord.SlashCommand) -> discord.SlashCommandGroup | None:
    """Findet die erste Parent-Gruppe mit Permissions."""
    if PYCORD:
        while cmd and cmd.default_member_permissions is None:
            cmd = cmd.parent
        return cmd.default_member_permissions if cmd else None
    else:
        while cmd and cmd.default_permissions is None:
            cmd = cmd.parent
        return cmd.default_permissions if cmd else None


async def pass_checks(command: discord.SlashCommand, ctx) -> bool:
    """Prüft alle Checks für einen Command."""
    for check in deepcopy(command.checks):
        try:
            if inspect.iscoroutinefunction(check):
                await check(ctx)
            else:
                if not check(ctx):
                    return False
        except Exception:
            return False
    return True


class Help(Cog, hidden=True):
    """Das Haupt-Help-Menü für NovaCord."""

    def __init__(self, bot: Bot):
        super().__init__(bot)
        if PYCORD:
            if bot.help.contexts:
                self.help.contexts = bot.help.contexts
            if bot.help.integration_types:
                self.help.integration_types = bot.help.integration_types
        else:
            self.help.guild_only = bot.help.guild_only

    @slash_command(name=tr("cmd_name"), description=tr("cmd_description"))
    async def help(self, ctx):
        interaction = ctx.interaction if PYCORD else ctx

        # Standard-Embed, wenn nichts gesetzt ist
        embed = self.bot.help.embed
        if embed is None:
            embed = discord.Embed(
                title="📘 NovaCord Hilfe",
                description="Wähle unten eine Kategorie aus, um Befehle anzuzeigen.",
                color=discord.Color.blue()
            )
            embed.set_footer(text="NovaCord Help Menu")
            embed.set_author(name=str(ctx.user), icon_url=getattr(ctx.user.avatar, "url", None))

        # Übersetzungen laden
        locale = I18N.get_locale(ctx)
        try:
            embed_overrides = I18N.localizations[locale]["help"]["embed"]
        except (KeyError, AttributeError):
            embed_overrides = {}

        for key, value in embed_overrides.items():
            setattr(embed, key, value)

        embed = replace_embed_values(
            embed, interaction, await fill_custom_variables(self.bot.help.kwargs)
        )

        options = []
        commands: dict[str, dict] = {}

        # Alle Cogs durchgehen
        for name, cog in self.bot.cogs.items():
            if getattr(cog, "hidden", False):
                continue

            group, name = get_group(cog, name, locale)
            if not name:
                continue

            if name not in commands:
                commands[name] = {"cmds": []}

            emoji = get_emoji(cog)
            commands[name]["emoji"] = emoji
            desc = get_cog_desc(cog, locale) or tr("default_description", name, use_locale=ctx)

            if not desc:
                desc = "Keine Beschreibung verfügbar."

            commands[name]["description"] = desc
            field_name = replace_placeholders(self.bot.help.title, name=name, emoji=emoji)
            field_value = replace_placeholders(
                self.bot.help.description, description=desc, name=name, emoji=emoji
            )

            # Befehle sammeln
            cog_cmds = []
            if PYCORD:
                cog_cmds = [
                    cmd for cmd in cog.walk_commands()
                    if isinstance(cmd, discord.ApplicationCommand)
                    and type(cmd) not in [
                        discord.MessageCommand,
                        discord.UserCommand,
                        discord.SlashCommandGroup,
                    ]
                ]
            else:
                cog_cmds = cog.walk_app_commands()

            for command in cog_cmds:
                if self.bot.help.permission_check:
                    if PYCORD and not await pass_checks(command, ctx):
                        continue
                    if isinstance(ctx.user, discord.Member):
                        perms = command.default_member_permissions if PYCORD else command.default_permissions
                        if perms and not command.parent:
                            if not perms.is_subset(ctx.user.guild_permissions):
                                continue
                        parent_perms = get_perm_parent(command)
                        if parent_perms and not parent_perms.is_subset(ctx.user.guild_permissions):
                            continue

                if ctx.guild and getattr(command, "guild_ids", None):
                    if ctx.guild.id not in command.guild_ids:
                        continue

                commands[name]["cmds"].append(command)

            if not commands[name]["cmds"]:
                continue

            label = f"{name} ({len(commands[name]['cmds'])})" if self.bot.help.show_cmd_count else name
            options.append(discord.SelectOption(label=label, emoji=emoji, value=name))

            if self.bot.help.show_categories:
                embed.add_field(name=field_name, value=field_value, inline=False)

        if not options:
            return await ctx.response.send_message(
                tr("no_commands", use_locale=ctx), ephemeral=True
            )

        if len(options) > 25:
            options = options[:25]
        if len(embed.fields) > 25:
            embed.fields = embed.fields[:25]

        sorted_options = sorted(options, key=lambda x: x.label.lower())
        embed.fields = sorted(embed.fields, key=lambda x: x.name.lower())

        view = CategoryView(sorted_options, self.bot, ctx.user, commands, ctx)
        for button in self.bot.help.buttons:
            view.add_item(deepcopy(button))

        await ctx.response.send_message(embed=embed, view=view, ephemeral=self.bot.help.ephemeral)


class CategorySelect(discord.ui.Select):
    """Dropdown für Kategorien im Help-Menü."""

    def __init__(self, options, bot: Bot, member, commands, interaction):
        super().__init__(min_values=1, max_values=1,
                         placeholder=tr("placeholder", use_locale=interaction),
                         options=options)
        self.bot = bot
        self.member = member
        self.commands = commands

    def get_mention(self, cmd, locale: str) -> str:
        """SlashCommand zu einer Erwähnung oder Formatierung machen."""
        if self.bot.all_dpy_commands:
            for c in self.bot.all_dpy_commands:
                if c.name == cmd.name:
                    cmd = c
                    break

        if cmd.name_localizations is not discord.MISSING:
            default = cmd.name_localizations.get(locale, f"/{cmd.qualified_name}")
        else:
            default = f"/{cmd.qualified_name}"

        try:
            return cmd.mention or f"**{default}**"
        except AttributeError:
            return f"**{default}**"

    async def callback(self, interaction: discord.Interaction):
        if self.bot.help.author_only and interaction.user != self.member:
            return await emb.error(interaction, tr("wrong_user", use_locale=interaction))

        locale = I18N.get_locale(interaction)
        title = self.values[0]
        cmds = self.commands[title]
        emoji = cmds["emoji"]

        embed = self.bot.help.embed
        if embed is None:
            embed = discord.Embed(color=discord.Color.blue())
            embed.set_footer(text="NovaCord Help Menu")
        else:
            embed = replace_embed_values(
                embed, interaction, await fill_custom_variables(self.bot.help.kwargs)
            )

        embed.title = replace_placeholders(self.bot.help.title, name=title, emoji=emoji)
        embed.clear_fields()

        if self.bot.help.show_description:
            embed.description = cmds["description"] + "\n"

        commands = cmds["cmds"]
        style = self.bot.help.style

        if len(commands) > 25 and style in [HelpStyle.embed_fields, HelpStyle.codeblocks, HelpStyle.codeblocks_inline]:
            style = HelpStyle.embed_description

        if style == HelpStyle.embed_fields:
            for command in commands:
                embed.add_field(
                    name=f"**{self.get_mention(command, locale)}**",
                    value=f"`{get_cmd_desc(command, locale)}`",
                    inline=False
                )
        elif style == HelpStyle.codeblocks or style == HelpStyle.codeblocks_inline:
            for command in commands:
                embed.add_field(
                    name=f"**{self.get_mention(command, locale)}**",
                    value=f"```{get_cmd_desc(command, locale)}```",
                    inline=(style == HelpStyle.codeblocks_inline)
                )
        elif style == HelpStyle.embed_description:
            desc = embed.description or ""
            for command in commands:
                if len(desc) <= 3500:
                    desc += f"**{self.get_mention(command, locale)}**\n{get_cmd_desc(command, locale)}\n\n"
            embed.description = desc
        elif style == HelpStyle.markdown:
            desc = embed.description or ""
            for command in commands:
                if len(desc) <= 3500:
                    desc += f"### {self.get_mention(command, locale)}\n{get_cmd_desc(command, locale)}\n"
            embed.description = desc

        if not commands:
            embed.description = tr("no_commands", use_locale=interaction)

        view = CategoryView(self.options, self.bot, self.member, self.commands, interaction)
        for button in self.bot.help.buttons:
            view.add_item(deepcopy(button))
        await interaction.response.edit_message(embed=embed, view=view)


class CategoryView(View):
    """Haupt-View für das Help-Menü."""

    def __init__(self, options, bot: Bot, member, commands, interaction):
        if PYCORD:
            super().__init__(timeout=bot.help.timeout, disable_on_timeout=True)
        else:
            super().__init__(timeout=None)

        self.add_item(CategorySelect(options, bot, member, commands, interaction))
