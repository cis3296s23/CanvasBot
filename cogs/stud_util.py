import nextcord
import os
from dotenv import load_dotenv 
from nextcord.ext import commands
from nextcord import Interaction
from nextcord.ext.commands import has_permissions, MissingPermissions
import canvasapi
import json
import datetime 
import pytz
from pytz import timezone
from bs4 import BeautifulSoup

load_dotenv('../.env')

CANVAS = os.getenv("CANVAS")
BASEURL = 'https://templeu.instructure.com/'
canvas_api = canvasapi.Canvas(BASEURL, CANVAS)


class stud_util(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Our test server id. Change in the future.
    server_id = 1075559489631170590

    def get_user_canvas(self, member : nextcord.User | nextcord.Member,
                        filename = 'users.json') -> str:
        with open(filename, 'r+') as file:
            file_data = json.load(file)
            for user in file_data['users']:
                print(user['snowflake'])
                if user['snowflake'] == member.id:
                    return user['apikey']
            return "Please login using the /login command!"
            
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

    @nextcord.slash_command(name='weekly', description='view the upcoming assignments for the next 7 days.')
    async def view_grade(self, interaction : Interaction):
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
                if(due_date!='None'):
                    due_date = datetime.datetime.strptime(due_date, '%Y-%m-%dT%H:%M:%SZ')
                    time_diff = due_date - datetime.datetime.utcnow()
                    if 0<=time_diff.days <= 7:
                        if(time_diff.days==0):
                            out+=assignment.name + " is due today.\n"
                        elif(time_diff.days==1):
                            out+=assignment.name + " is due tomorrow.\n"
                        else:
                            out+=assignment.name + " is due in " + str(time_diff.days) + " days.\n"
                        
        await interaction.followup.send(out)

    @nextcord.slash_command(name='courses', description='List enrolled courses.')
    async def get_courses(self, interaction : Interaction):
        
        API_URL = 'https://templeu.instructure.com/'
        api_key = self.get_user_canvas(member=interaction.user)

        if api_key == 'Please login using the /login command!':
            await interaction.response.send_message(api_key)
            return
        
        user = canvasapi.Canvas(API_URL, api_key)
        courses = user.get_courses(enrollment_state='active')

        await interaction.response.send_message("Here are your courses:\n")

        select = 0
        output = ""
        for course in courses:
            name = course.name
            id = course.id
            output += f"({select}) {name}\n"
            select += 1

        output += "+ Enter a number to select the corresponding course +\n"
        await interaction.followup.send(f"```diff\n{output}```") 

        def check(message : nextcord.message):
            if message.content.isdigit():
                global pick 
                pick = int(message.content)
                return range(0,select).count(pick) > 0
            
        await self.client.wait_for('message', check=check, timeout = 15)
        print(courses[pick].id)
        global current_class 

        current_class = user.get_course(courses[pick].id)
        await interaction.followup.send(f'Current course: **{courses[pick].name}**\n')

    @nextcord.slash_command(name='announcements', description='View announcements from current class')
    async def display_announcements(self, interaction : Interaction):
        await interaction.response.defer()
        test  = canvas_api.get_announcements(context_codes=[current_class])
        print(len(list(test)))
        if(len(list(test))==0):
            print("No announcements")
            return
        for a in test:
            html=a.message
            soup = BeautifulSoup(html, features="html.parser")
            for script in soup(["script", "style"]):
                script.extract()    # rip it out
            text = soup.get_text()
            str=a.title
            if(a.posted_at is not None):
                posted_at = datetime.datetime.strptime(a.posted_at, '%Y-%m-%dT%H:%M:%SZ')
                formatted_date = posted_at.strftime('%B %d, %Y at %I:%M %p')
                str+='\n'+formatted_date
                
            await interaction.followup.send(str+'\n'+text)
            break

def setup(client):
    client.add_cog(stud_util(client))
