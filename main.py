import discord
import keys
from discord.ext import commands
import canvasapi
import datetime 
import pytz

DISCORD = keys.tokens["discord"]
CANVAS = keys.tokens['canvas']
BASEURL = 'https://templeu.instructure.com/'
canvas_api = canvasapi.Canvas(BASEURL, CANVAS)

current_class = canvas_api.get_courses()[5]

bot = commands.Bot(command_prefix = "&", intents = discord.Intents.all())

@bot.event
async def on_ready():
    print("Canvas Info Bot up and running!")

@bot.command()
async def course(ctx):
    await ctx.send("Here are your courses:\n")

    courses = canvas_api.get_courses(enrollment_state='active')

    select = 0
    for course in courses:
        name = course.name
        id = course.id
        await ctx.send(f"({select}) {name}\n")
        select += 1

    await ctx.send(f"Enter a number to select the corresponding course\n") 

    def check(m):
        if m.content.isdigit():
            global pick 
            pick = int(m.content)
            return range(0,select).count(pick) > 0

    msg = await bot.wait_for('message', check=check, timeout = 15)
    print(courses[pick].id)
    global current_class 
    current_class = canvas_api.get_course(courses[pick].id)
    await ctx.send(f'Current course: **{courses[pick].name}**\n')

@bot.command()
async def upcoming(ctx):
    none_upcoming = True

    user = canvas_api.get_user('self')

    print(user.name)

    #softwareDesign = canvas_api.get_course(123654) 
    assignments = current_class.get_assignments()

    for assignment in assignments:
        due_date = str(assignment.due_at)

        if(due_date != "None"):
            t1 = datetime.datetime(int(due_date[0:4]), int(due_date[5:7]), int(due_date[8:10]))
            t2 = datetime.datetime.now()
            if(t1>t2):
                none_upcoming = False
                readable_time = f"{due_date[11:16]} UTC"
                readable_date = t1.strftime("%A, %B %d")
                print(f"{assignment} is due on {readable_date} at {readable_time}\n")
                await ctx.send(f"```diff\n- {assignment.name} -\ndue on {readable_date} at {readable_time}```\n\n")
    
    if(none_upcoming):
        await ctx.send(f"You have no upcoming assignments in {current_class.name}!")

bot.run(DISCORD)