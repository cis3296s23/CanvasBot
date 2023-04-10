import discord
import config
from discord.ext import commands
import canvasapi
import datetime 

TOKEN = config.tokens["discord"]
CHANNEL_ID = 1075559490289668201

bot = commands.Bot(command_prefix = "&", intents = discord.Intents.all())

@bot.event
async def on_ready():
    print("Canvas Info Bot up and running!")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Canvas Info Bot up and running!")
    
@bot.event
async def on_message(message):
    username = str(message.author).split("#")[0]
    channel = str(message.channel.name)
    user_message = str(message.content)
  
    if user_message.lower() =='help':
        await message.channel.send("Welcome to the Canvas Helper bot.  Here are the commands you can use: \n help - prints this message \n Announcements - prints the announcements for the course \n Grade - prints your current grade for a course \n Poll - creates a poll for a course")
        return

@bot.command()
async def courses(ctx):
    TOKEN2=config.tokens['canvas']
    BASEURL='https://templeu.instructure.com/'
    canvas_api = canvasapi.Canvas(BASEURL, TOKEN2)
    user = canvas_api.get_user('self')
    courses=user.get_courses()
    #iterates through courses
    for course in courses:
        try:
            #split to get the year of the course
            date=course.created_at.split('-')[0]
            #print(date)
            courselist=[]
            #
            if(int(date)==2023):
                
                await ctx.send(course)
                
                courselist.add(course)
            
        except AttributeError:
            print("error")
    
@bot.command()
async def upcoming(ctx):
    TOKEN2 = config.tokens['canvas']
    BASEURL = 'https://templeu.instructure.com/'

    canvas_api = canvasapi.Canvas(BASEURL, TOKEN2)

    user = canvas_api.get_user('self')

    print(user.name)

    softwareDesign = canvas_api.get_course(123654) 
    assignments = softwareDesign.get_assignments()

    for assignment in assignments:
        due_date = str(assignment.due_at)

        readable = due_date
        if(due_date != "None"):
            t1 = datetime.datetime(int(due_date[0:4]), int(due_date[5:7]), int(due_date[8:10]))
            t2 = datetime.datetime.now()
            if(t1>t2):
                readable_date = f"{due_date[5:10]}-{due_date[0:4]}"
                readable_time = f"{due_date[11:16]} UTC"
                print(f"{assignment} is due on {readable_date} at {readable_time}\n")
                await ctx.send(f"{assignment}\n **due on {readable_date} at {readable_time}**\n\n")
@bot.command()
async def help(ctx):
    await ctx.send("Welcome to the Canvas Helper bot.  Here are the commands you can use:\nhelp - prints this message\nAnnouncements - prints the announcements for the course\nGrade - prints your current grade for a course\nPoll - creates a poll for a course")


bot.run(TOKEN)
