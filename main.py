import discord
from discord.ext import commands
import random
from API_keys import diceMocker
import diceMockeries
import flattries

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='/', intents=intents)


def get_random_message():
    return random.choice(diceMockeries.combat_failures)


def get_flattery():
    return random.choice(flattries.combat_success)


async def lost(ctx):
    message = get_random_message()
    await ctx.send(message)


async def crit(ctx):
    message = get_flattery()
    await ctx.send(message)


@client.command(name="roll")
async def roll(ctx, num_rolls: int):
    if num_rolls <= 0:
        await ctx.send("Please roll at least one dice.")
        return

    results = [random.randint(1, 10) for _ in range(num_rolls)]
    successful_rolls = [roll for roll in results if roll >= 6]
    success_count = len(successful_rolls)
    count_tens = results.count(10)
    critical = count_tens // 2
    success_count += critical * 2

    await ctx.send(f"You rolled: {results}\nTotal: {success_count} and {successful_rolls}")

    if success_count == 0:
        await lost(ctx)
    elif critical > 0:
        await crit(ctx)


client.run(diceMocker)
