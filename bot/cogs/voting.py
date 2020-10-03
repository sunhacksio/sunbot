from discord.ext import commands
import discord
import aiohttp
import os

SERVER = os.getenv("SERVER")
SECRET = os.getenv("SUNBOT_SECRET")


STR_UNVERIFIED = """
We weren't able to verify you checked in! Voting for hacker's choice is only available to participants. If you believe this is an error reach out to us in the #ask-sunhacks channel!
"""

STR_OPENING = """
🗳 sunhacks uses comparison voting to determine our hackers' choice award! \
If you aren't familiar with comparison voting systems (like Gavel) please \
read the instructions below!

Comparison voting works by comparing two projects and picking which is better. \
We will send you one project at a time and you will have to compare this with \
the previous. You will use emoji reactions to vote on the better project.

If you are shown a project that you feel may have cheated, please use the 🚩 \
reaction to report it. This will give you a different project to compare with \
your previous project.

To begin, did you submit a project on Devpost? **React with 👍 or 👎**
"""

STR_TABLE = """
Awesome! We love it when hackers submit their projects. To make sure you don't recieve your own project, **respond with your table number**! You can find it on Devpost here: <URL>
"""

STR_TABLE_INVALID = """
Weird... we didn't see that table. You can find your project's table number here <URL>. Please **respond with your table number**
"""

STRF_TABLE_FOUND = """
We found your project \"{0[title]}\"
"""

STR_DB_ERROR = """
There was an error writing your info to the database... Please try re-reacting to the discord bot in the sunhacks server to restart.
"""

STR_START_VOTING = """
Let's start voting! We will show you projects one at a time and you will vote on the two most recent projects.

**Here is your first project to review!**
"""

STR_NO_PROJ = """
There are no projects to vote on at this time! Thanks for your help
"""

STRF_PROJECT = """
> {0[emoji]} - **{0[title]}**
> {0[url]}
"""

STR_REVIEW_PROJ = """
Review this project and press ➡️ to continue!
"""

STRF_FLAG_PROJ = """
We take cheating very seriously at sunhacks. What did you notice about \"{0[title]}\"? Please send one message with your report. Use `Shift+Enter` to make new lines if needed.
"""

STR_FLAG_SENT = """
Your report has been recorded and will be reviewed by the sunhacks team! Thank you for your help
"""

STRF_VOTE = """
**Which project is better?**

> {0[emoji]} - {0[title]}
> {1[emoji]} - {1[title]}
"""

STR_VOTE_SENT = """
Vote saved! Moving onto more projects...
"""

EMOJIS = ["🔴","🟦","🟢","🟨","🟣","🟥","🔵","🟩","🟡","🟪"]

pending_tasks = dict()


class Voting(commands.Cog):
    """Commands !"""
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.start_vote = 761769313270890537

    async def get_req(self, endpoint, params, data = None, error = ""):
        async with aiohttp.ClientSession() as session:
            headers = {"Sunbot-Secret" : SECRET}
            async with session.get(os.path.join(SERVER,endpoint), params = params, headers = headers, data = data) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return None

    async def post_req(self, endpoint, params, data = None, error = ""):
        async with aiohttp.ClientSession() as session:
            headers = {"Sunbot-Secret" : SECRET}
            async with session.post(os.path.join(SERVER,endpoint), params = params, headers = headers, data = data) as resp:
                if resp.status == 201:
                    return await resp.json()
                else:
                    return None

    async def send_react_req(self, member, message, emojis):
        msg = await member.send(message)
        for i in emojis:
            await msg.add_reaction(i)
        def check(reaction, user):
            return member == user and reaction.emoji in emojis
        if member.id in pending_tasks:
            pending_tasks[member.id].close()
        pending_tasks[member.id] = self.bot.wait_for(event = "reaction_add", check = check)
        reaction, user = await pending_tasks[member.id]
        for i in emojis:
            await msg.remove_reaction(i,self.bot.user)
        return reaction.emoji

    async def send_msg_req(self, member, message):
        msg = await member.send(message)
        def check(msg):
            return member == msg.author
        if member.id in pending_tasks:
            pending_tasks[member.id].close()
        pending_tasks[member.id] = self.bot.wait_for(event = "message", check = check)
        message = await pending_tasks[member.id]
        return message.content

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == self.start_vote:
            if payload.emoji.name == "🗳️":
                member = payload.member
                # Check if hacker checked in!
                res = await self.get_req("discord/verified",{"id" : member.id})
                if res['verified'] == "False":
                    await member.send(STR_UNVERIFIED)
                    return False
                # Send opening message!
                react = await self.send_react_req(member, STR_OPENING, ["👍","👎"])
                # If they have a table get their table number
                if react == "👍":
                    table = int(await self.send_msg_req(member, STR_TABLE))
                    res = await self.post_req("discord/startvote",{"id": member.id, "table": table})
                    # Loop if table was invalid
                    while res == None:
                        table = int(await self.send_msg_req(member, STR_TABLE_INVALID))
                        res = await self.post_req("discord/startvote",{"id": member.id, "table": table})
                    await member.send(STRF_TABLE_FOUND.format(res))
                # Just send the hacker's ID over
                else:
                    res = await self.post_req("discord/startvote",{"id": member.id})
                    if res == None:
                        await member.send(STR_DB_ERROR)
                        return False

                await member.send(STR_START_VOTING)
                round = 0
                while True:
                    next_proj = await self.get_project(member, round)
                    if next_proj == None:
                        await member.send(STR_NO_PROJ)
                        return True
                    try:
                        reviewed = await self.review_project(member, next_proj)
                    except:
                        return False
                    # If project wasn't flagged
                    if reviewed:
                        # Vote after round 0
                        if round != 0:
                            try:
                                await self.vote(member, prev_proj, next_proj)
                            except:
                                raise Exception()
                                return False
                        prev_proj = next_proj
                        round += 1

    async def vote(self, member, prev_proj, next_proj):
        emoji = await self.send_react_req(member, STRF_VOTE.format(prev_proj, next_proj), emojis = [prev_proj["emoji"], next_proj["emoji"]])
        params = {
            "id" : member.id,
            "next_table": next_proj["table"],
            "prev_table": prev_proj["table"],
            "next_won": str(emoji == next_proj["emoji"])
        }
        res = await self.post_req("discord/voteproj", params = params)
        if res == None:
            await member.send(STR_DB_ERROR)
            raise Exception("Unable to store data")
        await member.send(STR_VOTE_SENT)

    async def get_project(self, member, round):
        res = await self.get_req("discord/nextproj",{"id" : member.id})
        if res["table"] == None:
            return None
        res["emoji"] = EMOJIS[round % len(EMOJIS)]
        return res

    async def review_project(self, member, proj):
        params = {
            "id" : member.id,
            "table" : proj["table"]
        }
        await member.send(STRF_PROJECT.format(proj))
        emoji = await self.send_react_req(member, STR_REVIEW_PROJ, ["➡️","🚩"])
        if emoji == "🚩":
            report = await self.send_msg_req(member, STRF_FLAG_PROJ.format(proj))
            res = await self.post_req("discord/flagproj", params = params, data = report)
            if res == None:
                await member.send(STR_DB_ERROR)
                raise Exception("Unable to store data")
            await member.send(STR_FLAG_SENT)
            return False
        else:
            res = await self.post_req("discord/viewproj", params = params)
            if res == None:
                await member.send(STR_DB_ERROR)
                raise Exception("Unable to store data")
            return True

def setup(bot):
    bot.add_cog(Voting(bot))
