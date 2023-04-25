import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord.ext.commands import has_permissions, MissingPermissions
from canvasapi import Canvas
from nextcord import SlashOption
import json




''' Cog for other utility commands such as help or logging in. Basically
    things that are not specifically for professor or student. ''' 
class other_util(commands.Cog):
    def __init__(self, client, user_count):
        self.client = client
        self.user_count = user_count

    # Our test server id. Change in the future.
    server_id = 1075559489631170590
    

    # Help command.
    @nextcord.slash_command(name='help', description='List command names and descriptions.', guild_ids=[server_id])
    async def help(self, interaction : Interaction):
        await interaction.response.send_message(f"Welcome to the Canvas Helper bot!  Here are the commands you can use: \
             \n help - prints this message \
             \n Announcements - prints the announcements for the course \
             \n Grade - prints your current grade for a course \
             \n Poll - creates a poll for a course", ephemeral=True)

    # Login command.
    @nextcord.slash_command(name='login', description='Login to Canvas.', guild_ids=[server_id])
    async def login(self, interaction : Interaction,
                    api_key : str = SlashOption(name='api_key',
                                                description="Your API Key")):
        
        if self.is_logged(api_key):
            await interaction.response.send_message('Already logged in!', ephemeral=True)
            return
        
        
        user_snowflake = interaction.user.id
        self.user_count = self.add_user(api_key=api_key, snowflake=user_snowflake, user_count=self.user_count)

        await interaction.response.send_message("Successfully logged in!")


    def is_logged(self, api_key : str, 
                  filename='users.json') -> bool:
        with open(filename, 'r+') as file:
            file_data = json.load(file)
            for user in file_data['users']:
                if user['apikey'] == api_key:
                    return True
            return False
    
    def add_user(self, api_key : str,
                       snowflake : nextcord.User.id,
                       user_count : int,
                       filename='users.json') -> int:
        with open(filename, 'r+') as file:
            file_data = json.load(file)
            new_user = {
                'id': user_count,
                'snowflake': snowflake,
                'apikey': api_key
            }
            file_data['users'].append(new_user)
            file.seek(0)
            json.dump(file_data, file, indent=4)

        return user_count + 1

        


def setup(client):
    client.add_cog(other_util(client, 0))