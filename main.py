import discord
from discord.ext import commands
import random
from API_keys import diceMocker
import diceMockeries
import flattries

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='/', intents=intents)


class RerollButton(discord.ui.Button):
    def __init__(self, pool, hunger, difficulty):
        super().__init__(label="Reroll Failures", style=discord.ButtonStyle.green)
        self.pool = pool
        self.hunger = hunger
        self.difficulty = difficulty

    async def callback(self, interaction: discord.Interaction):
        results, hunger_results = reroll_failures(self.pool, self.hunger, self.difficulty)

        new_results = results + hunger_results
        successful_rolls = [roll for roll in results if roll >= self.difficulty] + \
                           [hunger_roll for hunger_roll in hunger_results if hunger_roll >= self.difficulty]

        success_count = len(successful_rolls)
        count_tens = new_results.count(10)
        critical = count_tens // 2
        success_count += critical * 2

        result_str = ", ".join(map(str, new_results))
        successes_str = ", ".join(map(str, successful_rolls))

        hunger_embed = discord.Embed(title=f"Willpower Reroll for {interaction.user.name}",
                                     description="Here are your updated dice rolls:",
                                     color=discord.Color.red())
        hunger_embed.add_field(name="Regular Dice Results", value=", ".join(map(str, results)), inline=False)
        hunger_embed.add_field(name="Hunger Dice Results", value=", ".join(map(str, hunger_results)), inline=False)

        hunger_embed.add_field(name="Successful Rolls", value=successes_str, inline=False)
        hunger_embed.add_field(name="Total Successes", value=str(success_count), inline=False)

        if critical > 0:
            hunger_embed.add_field(name="CRIT!", value="You have Crit!", inline=True)

        if success_count < self.difficulty:
            message = get_random_message()
        elif success_count > self.difficulty:
            message = get_flattery()
        else:
            message = "Barely girl..."

        hunger_embed.add_field(name="Salt of the day:", value=message, inline=False)
        await interaction.response.edit_message(embed=hunger_embed)


def reroll_failures(pool, hunger, difficulty):
    results = [random.randint(1, 10) for _ in range(pool - hunger)]
    hunger_results = [random.randint(1, 10) for _ in range(hunger)]
    failed_rolls = [roll for roll in results + hunger_results if roll < difficulty]
    rerolled_results = [random.randint(1, 10) for _ in range(len(failed_rolls))]
    return results + rerolled_results, hunger_results


async def barely(ctx):
    await ctx.send("Barely phew!")


def get_random_message():
    return random.choice(diceMockeries.combat_failures)


def get_flattery():
    return random.choice(flattries.combat_success)


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
    hunger_embed.add_field(name="Total Successes", value=str(success_count), inline=True)

    if critical > 0:
        hunger_embed.add_field(name="CRIT!", value="You have Crit!", inline=True)

    reroll_button = RerollButton(pool, hunger, difficulty)
    view = discord.ui.View()
    view.add_item(reroll_button)

    if success_count < difficulty:
        message = get_random_message()
    elif success_count > difficulty:
        message = get_flattery()
    else:
        message = "Barely girl..."

    hunger_embed.add_field(name="Salt of the day:", value=message, inline=False)
    await ctx.send(embed=hunger_embed, view=view)


client.run(diceMocker)
