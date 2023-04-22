import discord
from bs4 import BeautifulSoup
from discord.ext import commands

import canvasapi
import datetime 
import pytz

DISCORD = ''
CANVAS = ''
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

    msg = await bot.wait_for('message', check=check, timeout = 30) #changed timeout to 30 seconds
    print(courses[pick].id)
    global current_class 
    current_class = canvas_api.get_course(courses[pick].id)
    await ctx.send(f'Current course: **{courses[pick].name}**\n')

@bot.command()
async def announcements(ctx):
    user = canvas_api.get_user('self')
    courses=user.get_courses()
    courselist=[]
    await ctx.send("Pick to see announcements from a course:\n")

    courses = canvas_api.get_courses(enrollment_state='active')

    select = 0
    for course in courses:
        try:
            date=course.created_at.split('-')[0]
            if(int(date)==2023):
                courselist.append(course)
                name = course.name
                id = course.id
                await ctx.send(f"({select}) {name}\n")
                select += 1
        except AttributeError:
            print('Error: AttributeError occurred.')
    
    #
    
    while(1): 
        await ctx.send(f"Enter a number to select the corresponding course, enter number 9 or wait 15 seconds to quit\n") 

        def check(m):
            if m.content.isdigit():
                global pick 
                pick = int(m.content)
                print(pick, "pick")
                return pick

        msg = await bot.wait_for('message', check=check, timeout = 15)
        #print(courselist[pick].name)
        #print(pick, "pick in while loop")
        #print(len(courselist), "len of courselist")
        print(int(pick))
        if(int(pick)==9):
            await ctx.send('quitting')
            return 
        if(pick>=len(courselist)):
            await ctx.send('invalid input')
            continue
        
        announce=courselist[pick]
        announce=[int(announce.id)]
        test  = canvas_api.get_announcements(context_codes=announce)
        print(len(list(test)))
        if(len(list(test))==0):
            print("No announcements")
            continue
        for a in test:
            html=a.message
            
            soup = BeautifulSoup(html, features="html.parser")
            for script in soup(["script", "style"]):
                script.extract()    # rip it out
            text = soup.get_text()
            if(a.posted_at is not None):
                posted_at = datetime.datetime.strptime(a.posted_at, '%Y-%m-%dT%H:%M:%SZ')
                formatted_date = posted_at.strftime('%B %d, %Y at %I:%M %p')
                await ctx.send(formatted_date)
            await ctx.send(a.title)
            await ctx.send(text)
        
@bot.command()
async def weekly(ctx):
    user = canvas_api.get_user('self')
    courses=user.get_courses(enrollment_state= 'active')
    courselist=[]
    assignmentslist=[]
    for course in courses:
        try:
            date=course.created_at.split('-')[0]
            if(int(date)==2023):
                print(course.name)
                courselist.append(course)
                
        except AttributeError:
            print('Error: AttributeError occurred.')
            
    for course in courselist:
        assignments = course.get_assignments(submission_state='unsubmitted')
        assignmentslist.append(assignments)
    out=""
    for courseAssignments in assignmentslist:
        for assignment in courseAssignments:
            due_date=str(assignment.due_at)
            #print(assignment.name)
            if(due_date!='None'):
                due_date = datetime.datetime.strptime(due_date, '%Y-%m-%dT%H:%M:%SZ')
                time_diff = due_date - datetime.datetime.utcnow()
                #print(assignment.name)
                if 0<=time_diff.days <= 7:
                    if(time_diff.days==0):
                        out+=assignment.name + " is due today.\n"
                        
                    elif(time_diff.days==1):
                        out+=assignment.name + " is due tomorrow.\n"
                    else:
                        out+=assignment.name + " is due in " + str(time_diff.days) + " days.\n"
                    
    await ctx.send(out)

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
