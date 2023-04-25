import nextcord
import os
from dotenv import load_dotenv 
from nextcord.ext import commands
from nextcord import Interaction
from nextcord.ext.commands import has_permissions, MissingPermissions
import canvasapi
import json
from datetime import datetime as dt
import pytz
from bs4 import BeautifulSoup



class stud_util(commands.Cog):
    def __init__(self, client, curr_course : canvasapi.course.Course):
        self.client = client
        self.curr_course = curr_course

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
        
        self.curr_course = user.get_course(courses[pick].id)
        await interaction.followup.send(f'Current course: **{courses[pick].name}**\n')

    @nextcord.slash_command(name='upcoming', description='List the upcoming assignments.')
    async def get_upcoming(self, interaction : Interaction):
        API_URL = 'https://templeu.instructure.com/'
        api_key = self.get_user_canvas(member=interaction.user)
        
        if api_key == 'Please login using the /login command!':
            await interaction.response.send_message(api_key)
            return
        if self.curr_course is None:
            await interaction.response.send_message('Please use `/courses` first and select a course!')
            return
        
        await interaction.response.defer()

        none_upcoming = True
        
        user = canvasapi.Canvas(API_URL, api_key)
 
        assignments = self.curr_course.get_assignments()
        output = f"**Upcoming assingments for {self.curr_course.name}**\n"

        for assignment in assignments:
            due_date = str(assignment.due_at)

            if due_date == 'None':
                continue
            print(due_date)
            t1 = dt(int(due_date[0:4]), int(due_date[5:7]), int(due_date[8:10]), int(due_date[11:13]), int(due_date[14:16]), tzinfo=pytz.utc)
            t2 = dt.now(pytz.utc)

            if t1 > t2:
                none_upcoming = False

                readable_time = t1.astimezone(pytz.timezone('US/Eastern')).strftime("%H:%M")
                readable_date = t1.strftime("%A, %B %d")

                print(f"{assignment} is due on {readable_date} at {readable_time}\n")
                output += f"```diff\n- {assignment.name} -\ndue on {readable_date} at {readable_time}```\n"
    
        if(none_upcoming):
            await interaction.followup.send(f"You have no upcoming assignments in {user.name}!")
        else: 
            await interaction.followup.send(f"{output}")

    @nextcord.slash_command(name='weekly', description='View the upcoming assignments for the next 7 days.')
    async def view_weekly_assignments(self, interaction : Interaction):
        await interaction.response.defer()

        API_URL = 'https://templeu.instructure.com/'
        api_key = self.get_user_canvas(member=interaction.user)

        if api_key == 'Please login using the /login command!':
            await interaction.response.send_message(api_key)
            return
        
        user = canvasapi.Canvas(API_URL, api_key)
        courses = user.get_courses(enrollment_state='active')

        course_dict = {}

        for course in courses:
            try:
                date = int(course.created_at.split('-')[0])
                if date == dt.now().year:
                    print(course.name)
                    course_dict[course] = course.get_assignments(submission_state='unsubmitted')
            except AttributeError:
                print('Error: AttributeError occurred.')

        out : str = ""

        for course, assignments in course_dict.items():
            for assignment in assignments:
                due_date = str(assignment.due_at)
                if due_date == 'None':
                    continue

                due_date = dt.strptime(due_date, '%Y-%m-%dT%H:%M:%SZ')
                time_diff = due_date - dt.utcnow()
                days = time_diff.days

                if days > 7 or days < 0:
                    continue
                elif days == 0:
                    out += f'{assignment.name} is due today.\n'
                elif days == 1:
                    out += f'{assignment.name} is due tomorrow.\n'
                else:
                    out += f'{assignment.name} is due in {days} days.\n'
                        
        await interaction.followup.send(out)

    @nextcord.slash_command(name='announcements', description='View announcements from current class')
    async def display_announcements(self, interaction : Interaction):
        await interaction.response.defer()
        test  = canvas_api.get_announcements(context_codes=[current_class])
        print(len(list(test)))
        if len(list(test)) == 0:
            print("No announcements")
            return
        
        html=a.message
        soup = BeautifulSoup(html, features="html.parser")
        for script in soup(["script", "style"]):
            script.extract()    # rip it out
        text = soup.get_text()
        output=a.title
        if(a.posted_at is not None):
            posted_at = datetime.datetime.strptime(a.posted_at, '%Y-%m-%dT%H:%M:%SZ')
            formatted_date = posted_at.strftime('%B %d, %Y at %I:%M %p')
            output+='\n'+formatted_date

        await interaction.followup.send(output+'\n'+text)
        

def setup(client):
    client.add_cog(stud_util(client))
