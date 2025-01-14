import discord
from discord.ext import commands
import random
from API_keys import diceMocker
import diceMockeries
import flattries
import dirtyTalk

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='/', intents=intents)


class RerollButton(discord.ui.Button):
    def __init__(self, pool, hunger, difficulty, failures, hunger_results, successes):
        super().__init__(label="Reroll Failures", style=discord.ButtonStyle.green)
        self.pool = pool
        self.hunger = hunger
        self.difficulty = difficulty
        self.failures = failures
        self.hunger_results = hunger_results
        self.successes = successes

    async def callback(self, interaction: discord.Interaction):

        reroll_len = 3 if len(self.failures) > 3 else len(self.failures)

        results = [random.randint(1, 10) for _ in range(reroll_len)]
        new_results = results + self.hunger_results

        successful_rolls = [roll for roll in new_results if roll >= 6]
        success_count = len(successful_rolls)
        count_tens = new_results.count(10)
        critical = count_tens // 2
        success_count += critical * 2

        result_str = ", ".join(map(str, new_results))
        successes_str = ", ".join(map(str, successful_rolls))

        rerolled_pairs = [f"{fail} > {rerolled}" for fail, rerolled in zip(self.failures[:reroll_len], results)]
        rerolled_str = ", ".join(rerolled_pairs)

        hunger_embed = discord.Embed(title=f"Willpower Reroll for {interaction.user.name}",
                                     description="Here are your updated dice rolls:",
                                     color=discord.Color.red())
        hunger_embed.add_field(name="Dice Rerolled", value=rerolled_str, inline=False)
        hunger_embed.add_field(name="Hunger Dice Results", value=", ".join(map(str, self.hunger_results)), inline=False)

        hunger_embed.add_field(name="Successful Rolls", value=successes_str, inline=False)
        hunger_embed.add_field(name="Total Successes", value=str(success_count + self.successes), inline=False)

        if critical > 0:
            hunger_embed.add_field(name="CRIT!", value="You have Crit!", inline=True)

        if success_count < self.difficulty:
            message = get_random_message()
        elif success_count > self.difficulty:
            message = get_flattery()
        else:
            message = "Barely girl..."

        hunger_embed.add_field(name="Salt of the day:", value=message, inline=False)
        self.disabled = True
        await interaction.response.edit_message(embed=hunger_embed, view=self.view)


async def barely(ctx):
    await ctx.send("Barely phew!")


def get_random_message():
    return random.choice(diceMockeries.combat_failures)


def get_rizz_fail():
    return random.choice(diceMockeries.rizz_failures)


def get_dirty_talk():
    return random.choice(dirtyTalk.dirty_talk_successes)


def get_flattery():
    return random.choice(flattries.combat_success)


@client.command(name="roll")
async def roll(ctx, pool: int, hunger: int = 0, difficulty: int = 6, style: str = None):
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
    critical = count_tens // 2
    success_count += critical * 2

    hunger_embed = discord.Embed(title="D10 Roll for " + username, description="Here are your dice rolls:",
                                 color=discord.Color.red())
    hunger_embed.add_field(name="Regular Dice Results", value=", ".join(map(str, results)), inline=False)

    hunger_embed.add_field(name="Hunger Dice Results", value=", ".join(map(str, hunger_results)), inline=False)
    hunger_embed.add_field(name="Total Successes", value=str(success_count), inline=True)

    if critical > 0:
        hunger_embed.add_field(name="CRIT!", value="You have Crit!", inline=True)

    failures = [roll for roll in results if roll < 6]

    if success_count < difficulty and style == "r":
        message = get_rizz_fail()
    elif success_count < difficulty:
        message = get_random_message()
    elif success_count > difficulty and style == "r":
        message = get_dirty_talk()
    elif success_count > difficulty:
        message = get_flattery()
    else:
        message = "Barely girl..."

    hunger_embed.add_field(name="Salt of the day:", value=message, inline=False)
    if len(failures) > 0:
        reroll_button = RerollButton(pool, hunger, difficulty, failures, hunger_results, success_count)
        view = discord.ui.View()
        view.add_item(reroll_button)
        await ctx.send(embed=hunger_embed, view=view)
    else:
        await ctx.send(embed=hunger_embed)


client.run(diceMocker)
