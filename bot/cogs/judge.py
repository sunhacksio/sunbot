from discord.ext import commands
import discord
import os

class Judge(commands.Cog):
    """Commands !"""
    def __init__(self, bot):
        self.bot = bot
        self.guild = 737845782992126032
        self.invite_code = os.getenv("JUDGE_URL")
        self.role_ids = [750436508871163951, 762804426170695684]

    def find_invite_by_code(self, invite_list, code):
        for inv in invite_list:
            if inv.code == code:
                return inv
        return None

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.get_guild(self.guild)
        self.invites = await guild.invites()
        self.roles = [guild.get_role(role) for role in self.role_ids]
        print("[JUDGE] Setup Judge Check-in!")

    @commands.Cog.listener()
    async def on_member_join(self,member):
        before = self.invites
        after = await member.guild.invites()
        for invite in before:
            code = self.find_invite_by_code(after, invite.code)
            if code != None and invite.uses < code.uses:
                if invite.code == self.invite_code:
                    await member.add_roles(*self.roles)
                    await member.send("Thanks for joining as a judge! If you have any questions reach out to anyone with the `organizer` role or send a ticket in the `#sunhacks-tickets` channel!")
                    print(f"[Judge] Member {member.name}#{member.discriminator} joined as judge")
                self.invites = after
                return True

def setup(bot):
    bot.add_cog(Judge(bot))
