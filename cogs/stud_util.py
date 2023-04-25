import nextcord
import os
from dotenv import load_dotenv 
from nextcord.ext import commands
from nextcord import Interaction
from nextcord.ext.commands import has_permissions, MissingPermissions
import canvasapi
import datetime 
import pytz
from pytz import timezone
from bs4 import BeautifulSoup

load_dotenv('../.env')

CANVAS = os.getenv("CANVAS")
BASEURL = 'https://templeu.instructure.com/'
canvas_api = canvasapi.Canvas(BASEURL, CANVAS)

current_class = canvas_api.get_courses(enrollment_state='active')[3]

class stud_util(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name='upcoming', description='List the upcoming assignments.')
    async def get_upcoming(self, interaction : Interaction):
        await interaction.response.defer()

        none_upcoming = True

        user = canvas_api.get_user('self')
        print(user.name)
 
        assignments = current_class.get_assignments()
        output = f"**Upcoming assingments for {current_class.name}**\n"
        for assignment in assignments:
            due_date = str(assignment.due_at)

            if(due_date != "None"):
                print(due_date)
                t1 = datetime.datetime(int(due_date[0:4]), int(due_date[5:7]), int(due_date[8:10]), int(due_date[11:13]), int(due_date[14:16]), tzinfo=pytz.utc)
                t2 = datetime.datetime.now(pytz.utc)
                if(t1>t2):
                    none_upcoming = False
                    readable_time = t1.astimezone(timezone('US/Eastern')).strftime("%H:%M")
                    readable_date = t1.strftime("%A, %B %d")
                    print(f"{assignment} is due on {readable_date} at {readable_time}\n")
                    output += f"```diff\n- {assignment.name} -\ndue on {readable_date} at {readable_time}```\n"
                    #await interaction.followup.send(f"```diff\n- {assignment.name} -\ndue on {readable_date} at {readable_time}```\n\n")
    
        if(none_upcoming):
            await interaction.followup.send(f"You have no upcoming assignments in {current_class.name}!")
        else: 
            await interaction.followup.send(f"{output}")

    @nextcord.slash_command(name='grades', description='View grade for a specific class.')
    async def view_grade(self, interaction : Interaction, course : str):
        pass

    @nextcord.slash_command(name='due', description='Get due date for a specific assignment.')
    async def get_due_date(self, interaction : Interaction, assignment : str):
        pass
    @nextcord.slash_command(name='courses', description='List enrolled courses.')
    async def get_courses(self, interaction : Interaction):
        #await interaction.response.send_message("Here are your courses:\n")
        await interaction.response.defer()
        
        user = canvas_api.get_user('self')
        print(user.name)

        courses = canvas_api.get_courses(enrollment_state='active')

        select = 0
        output = ""
        for course in courses:
            name = course.name
            id = course.id
            output += f"({select}) {name}\n"
            select += 1

        output += "+ Enter a number to select the corresponding course +\n"
        await interaction.followup.send(f"```diff\n{output}```") 

        def check(m):
            if m.content.isdigit():
                global pick 
                pick = int(m.content)
                print(pick)
                return range(0,select).count(pick) > 0

        msg = await self.client.wait_for('message', check=check, timeout = 15)
        print(courses[pick].id)
        global current_class 
        current_class = canvas_api.get_course(courses[pick].id)
        await interaction.followup.send(f'Current course: **{courses[pick].name}**\n')

    @nextcord.slash_command(name='announcements', description='View announcement from current class')
    async def display_announcements(self, interaction : Interaction):
        await interaction.response.defer()
        test  = canvas_api.get_announcements(context_codes=[current_class])
        print(len(list(test)))
        if(len(list(test))==0):
            print("No announcements")
        output = ''
        for a in test:
            html=a.message
            
            soup = BeautifulSoup(html, features="html.parser")
            for script in soup(["script", "style"]):
                script.extract()    # rip it out
            text = soup.get_text()
            output += f'{a.title}\n'
            if(a.posted_at is not None):
                posted_at = datetime.datetime.strptime(a.posted_at, '%Y-%m-%dT%H:%M:%SZ')
                formatted_date = posted_at.strftime('%B %d, %Y at %I:%M %p')
                output += f'{formatted_date}\n'
            output += f"```{text}```"
            break

        await interaction.followup.send(output)

def setup(client):
    client.add_cog(stud_util(client))