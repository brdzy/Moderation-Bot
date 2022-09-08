from datetime import datetime, timezone, timedelta
import logging
import os
import hikari
from hikari import ActivityType, presences, ActivityTimestamps, ActivitySecret, ActivityAssets, ActivityFlag, ActivityParty, Activity, RichActivity, Status
import lightbulb
from dotenv import load_dotenv

load_dotenv()

bot = lightbulb.BotApp(
    os.getenv('TOKEN'),
    default_enabled_guilds=int(os.getenv('DEFAULT_GUILD_ID')),
    help_slash_command=True,
    intents=hikari.Intents.ALL,
)

bot.load_extensions_from('./plugins')

activity = Activity(
    name='lofi hip hop radio - beats to relax/study to',
    url='https://www.youtube.com/watch?v=jfKfPfyJRdk',
    type=ActivityType.STREAMING
    )

@bot.listen(lightbulb.LightbulbStartedEvent)
async def ready_listener(_):
    try:
        await bot.update_presence(activity=activity)
    except hikari.errors.ComponentStateConflictError:
        logging.warn('Could not change presence...')


def run() -> None:
    if os.name != 'nt':
        try:
            import uvloop
        except ImportError:
            logging.warn(
            'Failed to import uvloop! Remember to install it first! [pip install uvloop]'
            )
        else:
            uvloop.install()


if __name__ == '__main__':
    bot.run()
