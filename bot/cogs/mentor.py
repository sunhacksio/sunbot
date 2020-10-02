from discord.ext import commands
import discord
import os

class Mentor(commands.Cog):
    """Commands !"""
    def __init__(self, bot):
        self.bot = bot
        self.guild = 737845782992126032
        self.invite_code = os.getenv("MENTOR_URL")
        self.role_ids = [750436508871163951, 750435150227046471]

    def find_invite_by_code(self, invite_list, code):
        for inv in invite_list:
            if inv.code == code:
                return inv

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.get_guild(self.guild)
        self.invites = await guild.invites()
        self.roles = [guild.get_role(role) for role in self.role_ids]
        print("[MENTOR] Setup Mentor Check-in!")

    @commands.Cog.listener()
    async def on_member_join(self,member):
        before = self.invites
        after = await member.guild.invites()
        for invite in before:
            if invite.uses < self.find_invite_by_code(after, invite.code).uses:
                if invite.code == self.invite_code:
                    await member.add_roles(*self.roles)
                    await member.send("Thanks for joining as a mentor! If you have any questions reach out to anyone with the `organizer` role!")
                    print(f"[MENTOR] Member {member.name}#{member.discriminator} joined as mentor")
                self.invites = after
                return True

def setup(bot):
    bot.add_cog(Mentor(bot))
