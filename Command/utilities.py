from discord.ext import commands


class Utilities(commands.Cog):


    @commands.command()
    async def help(ctx):
        ctx.send("Welcome to the Canvas Helper bot.  Here are the commands you can use: \
             \n help - prints this message \
             \n Announcements - prints the announcements for the course \
             \n Grade - prints your current grade for a course \
             \n Poll - creates a poll for a course")


    async def announcement(message: str) -> str:
        return ""


    @commands.command()
    async def create_poll(ctx, arg):
        emojis = [':white_check_mark:', ':x:']
        await ctx.send(arg)
        for emoji in emojis:
            await ctx.add_reaction(emoji)
