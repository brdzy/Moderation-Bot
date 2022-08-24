import lightbulb
import hikari
from datetime import datetime
from lightbulb.utils import pag, nav
import psutil
import platform


information_plugin = lightbulb.Plugin('context_menu_commands')


@information_plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("serverinfo", "Show's the information of the current server", aliases=["si","servinfo"], auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def serverinfo(ctx: lightbulb.Context):
    guild = ctx.bot.cache.get_guild(ctx.guild_id) or await ctx.bot.rest.fetch_guild(ctx.guild_id)
    roles = await guild.fetch_roles()
    all_roles = [r.mention for r in roles]
    id = str(guild.id)
    created = int(guild.created_at.timestamp())
    owner = await guild.fetch_owner()
    members = len(guild.get_members().keys())
    verif = guild.verification_level.name.upper()
    role_count = len(guild.get_roles().keys())
    channels = len(guild.get_channels().keys())
    level = guild.premium_tier.value
    boost = guild.premium_subscription_count
    
    emb = hikari.Embed(title=f"Server info for {guild.name}", 
                    colour=ctx.author.accent_color,
                    timestamp=datetime.now().astimezone()
                    )
    
    emb.set_thumbnail(guild.icon_url)
    emb.set_image(guild.banner_url)
    emb.add_field(name="ID", value=id, inline=False)
    emb.add_field(name="Owner", value=f"{owner} ({owner.mention})", inline=False)
    emb.add_field(name="Created At", value=f"<t:{created}:d>\n(<t:{created}:R>)", inline=False)
    emb.add_field(name="Member Count", value=f"{members} Members", inline=False)
    emb.add_field(name="Channel Count", value=f"{channels} Channels", inline=False)
    emb.add_field(name="Verification Level", value=verif, inline=False)
    emb.add_field(name="Server Level", value=f"Level {level} ({boost} Boosts.)", inline=False)
        
    if "COMMUNITY" in guild.features:
        emb.add_field(name="Rule Channel", value=f"<#{guild.rules_channel_id}>", inline=False)
    if guild.afk_channel_id:
        emb.add_field(name="AFK Channel", value=f"<#{guild.afk_channel_id}> ({guild.afk_timeout})", inline=False)
    
    if guild.features:
        features = guild.features
        emb.add_field(name="Guild Features", value=", ".join(features).replace("_", " ").title(), inline=False)

    emb.add_field(name=f"Roles ({role_count})", value=", ".join(all_roles) if len(all_roles) < 10 else f"{len(all_roles)} roles", inline=False)
    await ctx.respond(embed=emb)


@information_plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("servericon", "Shows the servers icon", aliases=["si_icon"], auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def server_icon(ctx: lightbulb.Context):
    guild = ctx.bot.cache.get_guild(ctx.guild_id) or await ctx.bot.rest.fetch_guild(ctx.guild_id)
    embed = hikari.Embed(title=f"Server Icon for {guild.name}")
    embed.set_image(guild.icon_url)
    await ctx.respond(embed=embed)


@information_plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.option("role", "The role you want to view", hikari.Role)
@lightbulb.command("roleinfo", "Shows the list of member on a particular role", aliases=["roles","inr"], auto_defer=True, pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def inrole(ctx: lightbulb.Context, role: hikari.Role) -> None:
    try:
        lst = pag.EmbedPaginator()
        @lst.embed_factory()
        def build_embed(page_index,page_content):
            emb = hikari.Embed(title=f"List of members on the '{role.name}' Role.", description=page_content, color=role.color)
            return emb
    
        for member_id in ctx.get_guild().get_members():
            member = ctx.get_guild().get_member(member_id)
            if role.id in member.role_ids:
                lst.add_line(member)
            
        navigator = nav.ButtonNavigator(lst.build_pages())
        await navigator.run(ctx)
    except:
        await ctx.respond('Nobody has that role!')
        
        
stats_plugin = lightbulb.Plugin("stats", "Statistics of this bot", include_datastore = True)

stats_plugin.d.counter = datetime.now()

def solveunit(input):
    output = ((input // 1024) // 1024) // 1024
    return int(output)

@stats_plugin.command()
@lightbulb.command("stats", "Get statistics info of the bot.", auto_defer = True)
@lightbulb.implements(lightbulb.SlashCommand)
async def stats(ctx: lightbulb.Context) -> None:
    """Bot stats."""
    try:
        mem_usage = "{:.2f} MiB".format(
            __import__("psutil").Process(
            ).memory_full_info().uss / 1024 ** 2
        )
    except AttributeError:
        # OS doesn't support retrieval of USS (probably BSD or Solaris)
        mem_usage = "{:.2f} MiB".format(
            __import__("psutil").Process(
            ).memory_full_info().rss / 1024 ** 2
        )
    freq = psutil.cpu_freq(percpu=False).current
    sysboot = datetime.fromtimestamp(psutil.boot_time()).strftime("%B %d, %Y at %I:%M:%S %p")
    uptime = datetime.now() - stats_plugin.d.counter
    hours, rem = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(rem, 60)
    days, hours = divmod(hours, 24)
    guilds = ctx.bot.cache.get_guilds_view()
    users = ctx.bot.cache.get_users_view()
    channels = ctx.bot.cache.get_guild_channels_view()
    
    if days:
        time = "%s days, %s hours, %s minutes, and %s seconds" % (
            days,
            hours,
            minutes,
            seconds,
        )
    else:
        time = "%s hours, %s minutes, and %s seconds" % (
            hours, minutes, seconds)
    em = hikari.Embed(title="System Status", color=0x32441C)
    em.add_field(
        name=":desktop: CPU Usage",
        value=f"{psutil.cpu_percent():.2f}% ({psutil.cpu_count(logical=False)} Cores / {psutil.cpu_count(logical=True)} Threads) ({'{:0.2f}'.format(freq)} MHz) \nload avg: {psutil.getloadavg()}",
        inline=False,
    )
    em.add_field(
        name=":computer: System Memory Usage",
        value=f"**{psutil.virtual_memory().percent}%** Used",
        inline=False,
    )
    em.add_field(
        name=":dna: Kernel Version",
        value=platform.platform(aliased=True, terse=True),
        inline=False,
    )
    em.add_field(
        name=":gear: Library version",
        value=f"hikari {hikari.__version__} + Lightbulb {lightbulb.__version__}",
        inline=False,
    )
    em.add_field(
        name="\U0001F4BE BOT Memory usage",
        value=mem_usage,
        inline=False
    )
    em.add_field(
        name=":minidisc: Disk Usage",
        value=f"Total Size: {solveunit(psutil.disk_usage('/').total)} GB \nCurrently Used: {solveunit(psutil.disk_usage('/').used)} GB",
        inline=False,
    )
    em.add_field(
        name="\U0001F553 BOT Uptime",
        value=time,
        inline=False
    )
    em.add_field(
        name="⏲️ Last System Boot Time",
        value=sysboot,
        inline=False
    )
    em.add_field(
        name="🛰️ Servers (Guilds)",
        value=str(len(guilds)),
        inline=False
    )
    em.add_field(
        name="🚩 Channels",
        value=str(len(channels)),
        inline=False
    )
    em.add_field(
        name="👥 Users",
        value=str(len(users)),
        inline=False
    )
    await ctx.respond(em)


def load(bot):
    bot.add_plugin(information_plugin)
    bot.add_plugin(stats_plugin)