import asyncio
import re
import discord
from discord.ext import commands
from discord import app_commands

from utils.database import get_setting, save_setting

PANEL_COLOR = discord.Color.from_rgb(88, 200, 255)
TICKET_COLOR = discord.Color.red()

TICKET_TYPES = {
    "general": {
        "label": "General Support",
        "emoji": "<:vinfo:1568995804184584373>",
        "description": "Questions about the server, account, gameplay or community.",
    },
    "report": {
        "label": "Player Reports",
        "emoji": "<:valert:1568994115855720637>",
        "description": "Report cheaters, rule breakers or disruptive players. Evidence is required.",
    },
    "bug": {
        "label": "Bug Reports",
        "emoji": "<:vwarning:1568994546707071117>",
        "description": "Report glitches, technical issues or server exploits.",
    },
    "claims": {
        "label": "Claims & Perks",
        "emoji": "<:vice_money:1568994279047565423>",
        "description": "Missing rewards, ranks, purchases or other server perks.",
    },
    "appeal": {
        "label": "Ban Appeals",
        "emoji": "📕",
        "description": "Appeal a punishment and request a staff review.",
    },
    "partnership": {
        "label": "Partnerships",
        "emoji": "<a:vGirlzz:1568994184608878734>",
        "description": "Interested in partnering with VOLCANO SMP? Tell us about your community or server.",
    },
}


def panel_header_text():
    return (
        "# <:molten:1568996225800347708> VOLCANO SMP — SUPPORT CENTER\n"
        "Need assistance? Open a ticket by selecting the category that best matches "
        "your issue. Our staff team will review your request and assist you as soon as possible."
    )


def panel_footer_text():
    return (
        "### <:v8526link:1568994736067313705> Please Note\n"
        "• Provide clear and accurate information.\n"
        "• Include screenshots or video evidence when relevant.\n"
        "• Do not spam tickets or submit false reports.\n"
        "• Be respectful towards our staff team.\n\n"
        "**False reports or ticket abuse may result in punishment.**\n\n"
        "*Thank you for being part of Volcano SMP. <:v_volcano:1568996630265598154>*"
    )


class TicketModal(discord.ui.Modal):
    def __init__(self, ticket_type: str):
        self.ticket_type = ticket_type
        info = TICKET_TYPES[ticket_type]
        super().__init__(title=f"{info['label']} — Ticket")

        self.subject = discord.ui.TextInput(
            label="Subject",
            placeholder="Briefly describe your issue",
            max_length=100,
        )
        self.details = discord.ui.TextInput(
            label="Details",
            placeholder="Please provide clear and complete information.",
            style=discord.TextStyle.paragraph,
            max_length=2000,
        )
        self.add_item(self.subject)
        self.add_item(self.details)

        self.extra = None
        extra_fields = {
            "report": ("Evidence (optional)", "Paste screenshot/video links if available."),
            "bug": ("Steps to reproduce", "Explain what you did before the issue happened."),
            "claims": ("Reward / purchase details", "Tell us what reward, rank or perk is missing."),
            "appeal": ("Punishment details", "Explain your punishment and why it should be reviewed."),
            "partnership": ("Server / community details", "Tell us about your community and partnership proposal."),
        }
        if ticket_type in extra_fields:
            label, placeholder = extra_fields[ticket_type]
            self.extra = discord.ui.TextInput(
                label=label,
                placeholder=placeholder,
                style=discord.TextStyle.paragraph,
                required=ticket_type != "report",
                max_length=1000,
            )
            self.add_item(self.extra)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message("❌ Tickets can only be opened inside the server.", ephemeral=True)

        # One open ticket per user.
        for channel in guild.text_channels:
            if channel.topic and channel.topic.startswith(f"volcano_ticket:{interaction.user.id}:"):
                return await interaction.response.send_message(
                    f"❌ You already have an open ticket: {channel.mention}",
                    ephemeral=True,
                )

        settings = await get_setting(guild.id)
        category_id = settings[1] if settings else None
        support_role_id = settings[2] if settings else None
        category = guild.get_channel(category_id) if category_id else None
        support_role = guild.get_role(support_role_id) if support_role_id else None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True,
                attach_files=True, embed_links=True,
            ),
        }
        me = guild.me
        if me:
            overwrites[me] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True,
                manage_messages=True, manage_channels=True,
            )
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True,
                attach_files=True, embed_links=True,
            )

        safe_name = re.sub(r"[^a-z0-9-]", "-", interaction.user.name.lower()).strip("-") or "member"
        channel_name = f"{self.ticket_type}-{safe_name}"[:90]

        try:
            channel = await guild.create_text_channel(
                channel_name,
                category=category if isinstance(category, discord.CategoryChannel) else None,
                overwrites=overwrites,
                topic=f"volcano_ticket:{interaction.user.id}:{self.ticket_type}",
                reason=f"VOLCANO SMP ticket opened by {interaction.user}",
            )
        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ I need **Manage Channels** permission to create tickets.",
                ephemeral=True,
            )
        except discord.HTTPException as error:
            return await interaction.response.send_message(
                f"❌ Could not create the ticket: `{error}`",
                ephemeral=True,
            )

        info = TICKET_TYPES[self.ticket_type]
        embed = discord.Embed(
            title=f"{info['emoji']} {info['label']}",
            description=(
                f"Welcome {interaction.user.mention}!\n\n"
                "Your request has been submitted. A staff member will assist you as soon as possible."
            ),
            color=TICKET_COLOR,
        )
        embed.add_field(name="📝 Subject", value=self.subject.value, inline=False)
        embed.add_field(name="📋 Details", value=self.details.value, inline=False)
        if self.extra and self.extra.value:
            embed.add_field(name="📌 Additional Information", value=self.extra.value, inline=False)
        embed.set_footer(text=f"VOLCANO SMP • Ticket opened by {interaction.user}")

        mentions = interaction.user.mention
        if support_role:
            mentions = f"{support_role.mention} {mentions}"

        await channel.send(content=mentions, embed=embed, view=TicketControlView())
        await interaction.response.send_message(
            f"✅ Your ticket has been created: {channel.mention}",
            ephemeral=True,
        )


class TicketOpenButton(discord.ui.Button):
    def __init__(self, ticket_type: str):
        super().__init__(
            label="Open",
            style=discord.ButtonStyle.success,
            custom_id=f"volcano_open_{ticket_type}",
        )
        self.ticket_type = ticket_type

    async def callback(self, interaction: discord.Interaction):
        if interaction.guild is None:
            return await interaction.response.send_message("❌ Tickets can only be opened in the server.", ephemeral=True)
        for channel in interaction.guild.text_channels:
            if channel.topic and channel.topic.startswith(f"volcano_ticket:{interaction.user.id}:"):
                return await interaction.response.send_message(
                    f"❌ You already have an open ticket: {channel.mention}",
                    ephemeral=True,
                )
        await interaction.response.send_modal(TicketModal(self.ticket_type))


class TicketPanel(discord.ui.LayoutView):
    """Discord Components v2 ticket panel with each Open button on the right."""

    def __init__(self):
        super().__init__(timeout=None)

        items = [
            discord.ui.TextDisplay(panel_header_text()),
            discord.ui.Separator(),
            discord.ui.TextDisplay("## <:v68223developerrubyshiny:1568994405027807253> SUPPORT CATEGORIES"),
        ]

        for ticket_type, info in TICKET_TYPES.items():
            text = discord.ui.TextDisplay(
                f"**{info['emoji']} {info['label']}**\n{info['description']}"
            )
            button = TicketOpenButton(ticket_type)
            items.append(discord.ui.Section(text, accessory=button))
            if ticket_type != list(TICKET_TYPES.keys())[-1]:
                items.append(discord.ui.Separator())

        items.extend([
            discord.ui.Separator(),
            discord.ui.TextDisplay(panel_footer_text()),
        ])

        self.add_item(discord.ui.Container(*items, accent_colour=PANEL_COLOR))


class CloseTicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Close Ticket",
            emoji="🔒",
            style=discord.ButtonStyle.danger,
            custom_id="volcano_close_ticket",
        )

    async def callback(self, interaction: discord.Interaction):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel) or not channel.topic or not channel.topic.startswith("volcano_ticket:"):
            return await interaction.response.send_message("❌ This is not a VOLCANO SMP ticket.", ephemeral=True)

        parts = channel.topic.split(":")
        try:
            owner_id = int(parts[1])
        except (IndexError, ValueError):
            owner_id = 0

        settings = await get_setting(interaction.guild.id)
        support_role = interaction.guild.get_role(settings[2]) if settings and settings[2] else None
        allowed = (
            interaction.user.id == owner_id
            or interaction.user.guild_permissions.administrator
            or (support_role is not None and support_role in interaction.user.roles)
        )
        if not allowed:
            return await interaction.response.send_message("❌ You do not have permission to close this ticket.", ephemeral=True)

        await interaction.response.send_message("🔒 Ticket will close in **5 seconds**.")
        await asyncio.sleep(5)
        try:
            await channel.delete(reason=f"Ticket closed by {interaction.user}")
        except discord.HTTPException:
            pass


class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CloseTicketButton())


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # Persistent views must be registered once the cog is loaded.
        self.bot.add_view(TicketPanel())
        self.bot.add_view(TicketControlView())

    ticket = app_commands.Group(name="ticket", description="VOLCANO SMP ticket system")

    @ticket.command(name="panel", description="Send the VOLCANO SMP support panel")
    @app_commands.checks.has_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction):
        await interaction.channel.send(view=TicketPanel())
        await interaction.response.send_message("✅ Ticket panel sent successfully!", ephemeral=True)

    @ticket.command(name="category", description="Set the category where tickets are created")
    @app_commands.checks.has_permissions(administrator=True)
    async def category(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        await save_setting(interaction.guild.id, ticket_category_id=category.id)
        await interaction.response.send_message(f"✅ Ticket category set to **{category.name}**.", ephemeral=True)

    @ticket.command(name="supportrole", description="Set the staff role that can view tickets")
    @app_commands.checks.has_permissions(administrator=True)
    async def supportrole(self, interaction: discord.Interaction, role: discord.Role):
        await save_setting(interaction.guild.id, support_role_id=role.id)
        await interaction.response.send_message(f"✅ Support role set to {role.mention}.", ephemeral=True)

    @ticket.command(name="settings", description="View current ticket settings")
    async def settings(self, interaction: discord.Interaction):
        settings = await get_setting(interaction.guild.id)
        category = f"<#{settings[1]}>" if settings and settings[1] else "Not set"
        role = f"<@&{settings[2]}>" if settings and settings[2] else "Not set"
        embed = discord.Embed(title="🌋 VOLCANO SMP • Ticket Settings", color=PANEL_COLOR)
        embed.add_field(name="Ticket Category", value=category, inline=False)
        embed.add_field(name="Support Role", value=role, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
