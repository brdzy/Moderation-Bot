import lightbulb
import hikari


plugin = lightbulb.Plugin('context_menu_commands')


@plugin.command()
@lightbulb.command('Joined Date', 'See when user joined!')
@lightbulb.implements(lightbulb.UserCommand)
async def puska_context_joined_date(ctx: lightbulb.UserContext) -> None:
    await ctx.respond(f'**{ctx.options.target.display_name}** joined at <t:{ctx.options.target.joined_at.timestamp():.0f}:f>', )


@plugin.listener(hikari.GuildMessageCreateEvent)
async def print_messages(event):
    print(event.content)


def load(bot):
    bot.add_plugin(plugin)