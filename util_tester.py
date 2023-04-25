import unittest
import canvasapi
import datetime 
from datetime import datetime
import pytz
from pytz import timezone
from bs4 import BeautifulSoup

BASEURL = 'https://templeu.instructure.com/'
canvas_api = canvasapi.Canvas(BASEURL, '9957~QYVLdfzX0iU1i4KgpMkJ4ld8xkaKt1psZgJ2j3CjM1ChYcOdcNljhOsLjgDMIk00')
current_class = canvas_api.get_courses(enrollment_state='active')[3]

def upcoming():
    none_upcoming = True
 
    assignments = current_class.get_assignments()
    output = f"**Upcoming assingments for {current_class.name}**\n"
    for assignment in assignments:
        due_date = str(assignment.due_at)

        if(due_date != "None"):
            t1 = datetime.datetime(int(due_date[0:4]), int(due_date[5:7]), int(due_date[8:10]), int(due_date[11:13]), int(due_date[14:16]), tzinfo=pytz.utc)
            t2 = datetime.datetime.now(pytz.utc)
            if(t1>t2):
                none_upcoming = False
                readable_time = t1.astimezone(timezone('US/Eastern')).strftime("%H:%M")
                readable_date = t1.strftime("%A, %B %d")
                output += f"```diff\n- {assignment.name} -\ndue on {readable_date} at {readable_time}```\n"
                    #await interaction.followup.send(f"```diff\n- {assignment.name} -\ndue on {readable_date} at {readable_time}```\n\n")
    
    if(none_upcoming):
        output = f"You have no upcoming assignments in {current_class.name}!"
    else: 
        output = f"{output}"
    return output

def courses():
    courses = canvas_api.get_courses(enrollment_state='active')

    select = 0
    output = ""
    for course in courses:
        name = course.name
        id = course.id
        output += f"({select}) {name}\n"
        select += 1

    return select

def announcements():
    current_class = canvas_api.get_courses(enrollment_state='active')[0]
    test  = canvas_api.get_announcements(context_codes=[current_class])
    print(len(list(test)))
    if(len(list(test))==0):
        return "No announcements"
    for a in test:
        html=a.message
            
        soup = BeautifulSoup(html, features="html.parser")
        for script in soup(["script", "style"]):
            script.extract()    # rip it out
        text = soup.get_text()
        
        if(a.posted_at is not None):
            posted_at = datetime.strptime(a.posted_at, '%Y-%m-%dT%H:%M:%SZ')
            formatted_date = posted_at.strftime('%B %d, %Y at %I:%M %p')   
        return a.title

class botTester(unittest.TestCase):
    def test_login(self):
        user = canvas_api.get_user('self')
        self.assertEqual('Giorgio Tatarelli', user.name)

    def test_upcoming(self):
        output = upcoming()
        self.assertEqual(output, 'You have no upcoming assignments in CST: Diversity, Equity & Inclusion (DEI)!')

    def test_courses(self):
        output = courses()
        self.assertEqual(7, output-1)
    
    def test_announcements(self):
        output = announcements()
        self.assertEqual("No announcements", output)


if __name__ == '__main__':
    unittest.main()