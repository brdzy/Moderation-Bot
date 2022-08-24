from datetime import datetime, timedelta, timezone
import lightbulb
from lightbulb.utils import pag, nav
import hikari   
from hikari.permissions import Permissions



plugin = lightbulb.Plugin('moderation_commands')


KICK_PERM = (Permissions.KICK_MEMBERS)
BAN_PERM = (Permissions.BAN_MEMBERS)
WARN_PERM = (Permissions.MODERATE_MEMBERS)
TIMEOUT_PERM = (Permissions.MODERATE_MEMBERS)


kick_plugin = lightbulb.Plugin('kick', 'kick user')
kick_plugin.add_checks(
    lightbulb.checks.has_guild_permissions(hikari.Permissions.KICK_MEMBERS),
    lightbulb.checks.bot_has_guild_permissions(hikari.Permissions.KICK_MEMBERS)
)


@kick_plugin.command()
@lightbulb.option('reason', 'reason for kicking user', str, required=False, modifier = lightbulb.commands.OptionModifier.CONSUME_REST)
@lightbulb.option('user', 'the user you want to kick', hikari.User, required=True)
@lightbulb.app_command_permissions(KICK_PERM)
@lightbulb.command('kick', 'kick user', auto_defer = True, pass_options = True)
@lightbulb.implements(lightbulb.SlashCommand)
async def kick(ctx: lightbulb.Context, user, reason):
    res = reason or f'No reason provided by {ctx.author.username}'
    await ctx.respond('Kicking **{user}**')
    await ctx.bot.rest.kick_member(user=user, guild=ctx.get_guild(), reason=res)
    await ctx.edit_last_response(f'Succsesfully kicked {user} for {res}!')
    

mute_plugin = lightbulb.Plugin('timeout', 'place user for a timeout')
mute_plugin.add_checks(
    lightbulb.checks.has_guild_permissions(hikari.Permissions.MODERATE_MEMBERS),
    lightbulb.checks.bot_has_guild_permissions(hikari.Permissions.MODERATE_MEMBERS)
)


@mute_plugin.command()
@lightbulb.option('reason', 'the reason for the mute', str, required=False,modifier = lightbulb.commands.OptionModifier.CONSUME_REST)
@lightbulb.option('days', 'mutes duration (days)', int, required=False, default=0)
@lightbulb.option('hour', 'duration (hour)', int, required=False, default=0)
@lightbulb.option('minute', 'duration (minute)', int, required=False, default=0)
@lightbulb.option('second', 'duration (second)', int, required=False, default=0)
@lightbulb.option('user', 'the user you want to mute', hikari.Member , required=True)
@lightbulb.app_command_permissions(TIMEOUT_PERM)
@lightbulb.command('mute', 'mute a member', auto_defer = True, pass_options = True)
@lightbulb.implements(lightbulb.SlashCommand)
async def timeout(ctx: lightbulb.Context, user: hikari.Member, second: int, minute: int, hour: int , days: int, reason: str):
    
    res = reason or f'No Reason Provided. By: {ctx.author}'
    
    now = datetime.now(timezone.utc)
    then = now + timedelta(days=days, hours=hour, minutes=minute, seconds=second)
    
    if (then - now).days > 28:
        await ctx.respond('You cant mute someone for more than 28 days')
        return
    
    if days == 0 and hour == 0 and minute == 0 and second == 0:
        await ctx.respond(f'Removing mute from **{user}**')
        txt = f'users: {user.mention} mute has been removed successfully!'
    else:
        await ctx.respond(f'Attempting to timeout **{user}**')
        txt = f'User: {user.mention} has been muted until <t:{int(then.timestamp())}:R>'
    await ctx.bot.rest.edit_member(user = user, guild = ctx.get_guild(), communication_disabled_until=then, reason=res)
    await ctx.edit_last_response(txt)
    

ban_plugin = lightbulb.Plugin('ban', 'Prepare the ban hammer!! (Please use it wisely')
ban_plugin.add_checks(
    lightbulb.checks.has_guild_permissions(hikari.Permissions.BAN_MEMBERS),
    lightbulb.checks.bot_has_guild_permissions(hikari.Permissions.BAN_MEMBERS),
    lightbulb.guild_only
    )

   
@ban_plugin.command()
@lightbulb.option('reason', 'the reason for banning the member', str, required=False, modifier = lightbulb.commands.OptionModifier.CONSUME_REST)
@lightbulb.option('delete_message', 'Delete the messages after the ban? (up to 7 days, leave empty or set to 0 to not delete)', int, min_value = 0, max_value = 7, default = 0 ,required=False)
@lightbulb.option('user', 'the user you want to ban', hikari.User , required=True)
@lightbulb.app_command_permissions(BAN_PERM, dm_enabled=False)
@lightbulb.command('ban', 'ban a member', auto_defer = True, pass_options = True)
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def ban(ctx: lightbulb.Context, user: hikari.User, delete_message: int, reason: str):
    res = reason or f'No Reason Provided. By {ctx.author.username}'
    delete = delete_message or 0
    await ctx.respond(f'Banning **{user.username}**')
    await ctx.bot.rest.ban_member(user = user, guild = ctx.get_guild(), reason = res, delete_message_days=delete)
    await ctx.edit_last_response(f'Succesfully banned {user} for {res}!')
    

@ban_plugin.command()
@lightbulb.option('user', 'the user you want to unban (Please use their user ID)', hikari.Snowflake, required=True)
@lightbulb.app_command_permissions(BAN_PERM)
@lightbulb.command('unban', 'unban a member', auto_defer = True, pass_options = True)
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def unban(ctx: lightbulb.Context, user: hikari.Snowflake, reason: str):
    await ctx.respond(f'Unbanning the user ID of **{user}**')
    await ctx.bot.rest.unban_member(user = user, guild = ctx.get_guild())
    await ctx.edit_last_response(f'Succesfully unbanned the ID of {user}!')

   
@ban_plugin.command()
@lightbulb.app_command_permissions(BAN_PERM)
@lightbulb.command('banlist', 'see the list of banned members in this server', auto_defer = True)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def banlist(ctx: lightbulb.Context):
    bans = await ctx.bot.rest.fetch_bans(ctx.get_guild())
    lst = pag.EmbedPaginator()
    
    @lst.embed_factory()
    def build_embed(page_index,page_content):
        emb = hikari.Embed(title='List of Banned Members', description=page_content)
        emb.set_footer(f'{len(bans)} Members in total.')
        return emb
    
    for n, users in enumerate(bans, start=1):
        lst.add_line(f"**{n}. {users.user}** ({users.reason or 'No Reason Provided.'})")
    navigator = nav.ButtonNavigator(lst.build_pages())
    await navigator.run(ctx)


def load(bot):
    bot.add_plugin(mute_plugin),
    bot.add_plugin(kick_plugin),
    bot.add_plugin(ban_plugin)
    