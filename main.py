import discord
from discord.ext import commands
import random
from API_keys import diceMocker
import diceMockeries
import flattries

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='/', intents=intents)


async def barely(ctx):
    await ctx.send("Barely phew!")


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
async def roll(ctx, pool: int, hunger: int = 0, difficulty: int = 6):
    username = ctx.author.name
    if pool <= 0:
        await ctx.send("Please roll at least one dice.")
        return

    if pool < hunger:
        hunger = pool
        hunger_results = [random.randint(1, 10) for _ in range(hunger)]
        results = []
    else:
        results = [random.randint(1, 10) for _ in range(pool - hunger)]
        hunger_results = [random.randint(1, 10) for _ in range(hunger)]
    successful_rolls = [roll for roll in results if roll >= 6] + [hunger_roll for hunger_roll in hunger_results
                                                                  if hunger_roll >= 6]
    new_results = results + hunger_results
    success_count = len(successful_rolls)
    count_tens = new_results.count(10)
    successes_str = ", ".join(map(str, successful_rolls))
    critical = count_tens // 2
    success_count += critical * 2

    result_str = ", ".join(map(str, new_results))

    hunger_embed = discord.Embed(title="D10 Roll for " + username, description="Here are your dice rolls:",
                                 color=discord.Color.red())
    hunger_embed.add_field(name="Regular Dice Results", value=", ".join(map(str, results)), inline=False)

    hunger_embed.add_field(name="Hunger Dice Results", value=", ".join(map(str, hunger_results)), inline=False)

    if critical > 0:
        hunger_embed.add_field(name="CRIT!", value="You have Crit!", inline=True)
    await ctx.send(embed=hunger_embed)

    if success_count < difficulty:
        await lost(ctx)
    elif success_count > difficulty:
        await crit(ctx)
    else:
        await barely(ctx)


client.run(diceMocker)
